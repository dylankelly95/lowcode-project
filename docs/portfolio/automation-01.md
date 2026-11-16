## Business problem
At the start, new users of my artist portfolio idea will fill out a Google Form if they're interested in signing up to the beta version of my app to create their free online artist portfolio. A confirmation email needs to be sent to them to let them know that their applicaiton is being reviewed and this is currently being done manually.
 
## Trigger
When a Google Form - Artist Portfolio Beta Sign Up - is submitted - will have to be a poll since the data will be collected on Google Sheets which doesn't support webhooks. The form will contain name, email, type of artist, links to exisitng work if applicable, status.
## Steps
1.Form repsonse arrives and Make receives this
2.Append a row to the "Artist Portfolio Beta Sign Up" sheet: name, email, type of artist, links to exisitng work if applicable, status
3.Send an acknowledgement email to the prospective user quoting a reference number
4.Make sure the app/form is somewhere online where the handler can access it
 
## Failure questions
- What if it fires twice?
Once the submission is created, Google Forms doesn't allow it to be fired twice, so it is not possible. Check this with the answer in the screenshot though
- What if a step fails halfway?
this is where he said that he put the filter in to not allow courses that aren't his to be added to the sheet
- What data crosses a third party, and is any of it personal?
