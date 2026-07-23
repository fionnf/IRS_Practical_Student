-- Suggest Replies.applescript
--
-- Entry point for the Mail "Suggest Replies" action: shows a few AI-generated
-- reply options for the selected message and drafts whichever one you pick.
-- Install as ~/Library/Scripts/Applications/Mail/Suggest Replies.scpt
-- (via install.sh) so it appears in Mail's Script menu, and can be assigned
-- a keyboard shortcut through an Automator Quick Action — see README.md.
--
-- Never sends anything automatically: it only opens a draft for you to review.

use AppleScript version "2.4"
use framework "Foundation"
use scripting additions
use core : script "AIMailCore"

on run
	set selInfo to core's getSelectedMessage()
	if selInfo is missing value then return

	set theMessage to theMessage of selInfo
	set theSender to theSender of selInfo
	set theSubject to theSubject of selInfo
	set theBody to theBody of selInfo

	set theJSON to core's buildJSONInput(theSender, theSubject, theBody)

	try
		set repliesList to core's runSuggestReplies(theJSON, missing value)
	on error errText
		display alert "AI Reply Error" message errText as critical
		return
	end try

	if (count of repliesList) is 0 then
		display alert "No Suggestions" message "Claude did not return any reply suggestions." as warning
		return
	end if

	-- Build short previews for the picker (full text can be long/multi-line).
	set previewOptions to {}
	repeat with i from 1 to count of repliesList
		set end of previewOptions to ("Option " & i & ":  " & core's firstLinePreview(item i of repliesList, 90))
	end repeat

	set userChoice to choose from list previewOptions with prompt "Pick a reply to open as a draft (you can edit it before sending):" with title "AI Suggested Replies" default items {item 1 of previewOptions}
	if userChoice is false then return -- user cancelled

	set chosenIndex to 0
	repeat with i from 1 to count of previewOptions
		if (item i of previewOptions) is (item 1 of userChoice) then
			set chosenIndex to i
			exit repeat
		end if
	end repeat
	if chosenIndex is 0 then return

	set chosenText to item chosenIndex of repliesList
	core's draftReply(theMessage, theSender, theSubject, chosenText)
end run
