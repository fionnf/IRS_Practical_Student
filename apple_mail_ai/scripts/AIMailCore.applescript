-- AIMailCore.applescript
--
-- Shared handlers used by "Suggest Replies.scpt" and "Quick Reply.scpt".
-- This file is compiled and installed as a Script Library
-- (~/Library/Script Libraries/AIMailCore.scpt) by install.sh, so it must be
-- installed *before* the two scripts that depend on it (`use core : script
-- "AIMailCore"` is resolved at compile time).
--
-- Responsibilities:
--   * Read the selected message in Apple Mail.
--   * Hand it to suggest_replies.py (installed under
--     ~/Library/Application Support/AppleMailAI/) as JSON on stdin.
--   * Parse the JSON reply-suggestions back out.
--   * Create a draft reply in Mail with the chosen suggestion — never sends.

use AppleScript version "2.4"
use framework "Foundation"
use scripting additions

-- Fixed install location for the Python backend + config, independent of
-- wherever this repo happens to live (it may be deleted after install.sh runs).
property pluginDir : (POSIX path of (path to home folder)) & "Library/Application Support/AppleMailAI/"

-- Read the single selected message in Mail.
-- Returns a record {theMessage, theSender, theSubject, theBody}, or
-- `missing value` if nothing is selected (after showing an alert).
on getSelectedMessage()
	tell application "Mail"
		set theSelection to selection
		if (count of theSelection) is 0 then
			display alert "No Message Selected" message "Select an email in Apple Mail, then try again." as warning
			return missing value
		end if
		set theMessage to item 1 of theSelection
		set theSender to sender of theMessage
		set theSubject to subject of theMessage
		try
			set theBody to content of theMessage
		on error
			set theBody to ""
		end try
	end tell
	return {theMessage:theMessage, theSender:theSender, theSubject:theSubject, theBody:theBody}
end getSelectedMessage

-- Build a JSON string {"sender":..., "subject":..., "body":...} using
-- NSJSONSerialization so arbitrary quotes/newlines/unicode in the email are
-- encoded safely (no manual shell/string escaping).
on buildJSONInput(theSender, theSubject, theBody)
	set theDict to current application's NSMutableDictionary's dictionary()
	(theDict's setObject:theSender forKey:"sender")
	(theDict's setObject:theSubject forKey:"subject")
	(theDict's setObject:theBody forKey:"body")
	set {theData, theError} to current application's NSJSONSerialization's dataWithJSONObject:theDict options:0 |error|:(reference)
	if theData is missing value then
		error "Could not encode the selected email as JSON."
	end if
	return current application's NSString's alloc()'s initWithData:theData encoding:(current application's NSUTF8StringEncoding)
end buildJSONInput

-- Write the JSON input to a temp file (avoids shell-escaping an arbitrary
-- email body directly into a `do shell script` command string).
on writeInputFile(theJSONString)
	set tempPath to (current application's NSTemporaryDirectory() as text) & "ai_mail_input_" & (random number from 100000 to 999999) & ".json"
	set ok to theJSONString's writeToFile:tempPath atomically:true encoding:(current application's NSUTF8StringEncoding) |error|:(missing value)
	if ok is false then
		error "Could not write a temporary input file for the AI reply request."
	end if
	return tempPath
end writeInputFile

-- Run suggest_replies.py with the given JSON input.
-- replyCount: an integer to request a specific number of suggestions,
--             or `missing value` to use the count from config.json.
-- Returns a list of AppleScript strings (the suggested reply bodies).
on runSuggestReplies(theJSONString, replyCount)
	set tempPath to my writeInputFile(theJSONString)
	set pythonScript to pluginDir & "suggest_replies.py"
	set countArg to ""
	if replyCount is not missing value then
		set countArg to " --count " & (replyCount as text)
	end if
	set shellCmd to "/usr/bin/python3 " & quoted form of pythonScript & countArg & " < " & quoted form of tempPath

	try
		set jsonOutput to do shell script shellCmd
	on error errText number errNum
		try
			do shell script "rm -f " & quoted form of tempPath
		end try
		error errText number errNum
	end try

	try
		do shell script "rm -f " & quoted form of tempPath
	end try

	return my parseReplies(jsonOutput)
end runSuggestReplies

-- Parse {"replies": ["...", "..."]} JSON text into an AppleScript list of strings.
on parseReplies(jsonOutput)
	set outputData to (current application's NSString's stringWithString:jsonOutput)'s dataUsingEncoding:(current application's NSUTF8StringEncoding)
	set {resultDict, theError} to current application's NSJSONSerialization's JSONObjectWithData:outputData options:0 |error|:(reference)
	if resultDict is missing value then
		error "Could not parse the reply suggestions returned by Claude."
	end if
	set repliesNS to resultDict's valueForKey:"replies"
	set repliesList to {}
	if repliesNS is missing value then return repliesList
	repeat with i from 0 to ((repliesNS's |count|()) - 1)
		set end of repliesList to ((repliesNS's objectAtIndex:i) as text)
	end repeat
	return repliesList
end parseReplies

-- First line of `t`, trimmed to maxLen characters, for use as a preview
-- label in a `choose from list` dialog.
on firstLinePreview(t, maxLen)
	set savedTIDs to AppleScript's text item delimiters
	set AppleScript's text item delimiters to {linefeed, return}
	set ln to text item 1 of t
	set AppleScript's text item delimiters to savedTIDs
	if (length of ln) > maxLen then set ln to (text 1 thru maxLen of ln) & "…"
	return ln
end firstLinePreview

-- Create a draft reply to theMessage containing chosenText, and bring it to
-- the front for review. Never sends anything.
on draftReply(theMessage, theSender, theSubject, chosenText)
	tell application "Mail"
		activate
		try
			set theReply to reply theMessage opening window yes
			try
				set existingContent to content of theReply
			on error
				set existingContent to ""
			end try
			set content of theReply to chosenText & return & return & existingContent
		on error
			-- Fallback: Mail's `reply` command failed (e.g. message no longer
			-- available) — compose a fresh message addressed to the sender.
			try
				set theReply to make new outgoing message with properties {subject:"Re: " & theSubject, content:chosenText, visible:true}
				tell theReply
					make new to recipient at end of to recipients with properties {address:theSender}
				end tell
			on error errText2
				display alert "AI Reply Error" message "Could not create a draft reply: " & errText2 as critical
			end try
		end try
	end tell
end draftReply
