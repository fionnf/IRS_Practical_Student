-- Quick Reply.applescript
--
-- Entry point for the fast "auto response" shortcut: generates a single AI
-- reply for the selected message and opens it straight as a draft — no
-- picker. Install as ~/Library/Scripts/Applications/Mail/Quick Reply.scpt
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
		set repliesList to core's runSuggestReplies(theJSON, 1)
	on error errText
		display alert "AI Reply Error" message errText as critical
		return
	end try

	if (count of repliesList) is 0 then
		display alert "No Suggestion" message "Claude did not return a reply suggestion." as warning
		return
	end if

	set chosenText to item 1 of repliesList
	core's draftReply(theMessage, theSender, theSubject, chosenText)
end run
