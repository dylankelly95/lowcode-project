# Week 2 — AI Tool Comparison
 
## The requirement
We were required to implement a contact form route at /contact on our Flask application using standard Python tools. The form must take name, email, and message inputs, perform server-side validation to reject empty fields and malformed email addresses, display clear error feedback to the user, and redirect successful submissions to a confirmation page without storing data.
 
## Prompts used
### ChatGPT
I want a contact form for a Flask 3.x web application.
- render at /contact with fields for name, email and message
- validate that the email address is well-formed server side
- reject empty name or message fields with a visible error
- on success, show a confirmation page
Do not use any package outside Flask and the Python standard library

we dont need to store any data at the moment 

Run it and show me a preview I can test please
### Gemini
I want a contact form for a Flask 3.x web application.

render at /contact with fields for name, email and message
validate that the email address is well-formed server side
reject empty name or message fields with a visible error
on success, show a confirmation page
Do not use any package outside Flask and the Python standard library

we dont need to store any data at the moment

### Claude
I want a contact form for a Flask 3.x web application.

render at /contact with fields for name, email and message
validate that the email address is well-formed server side
reject empty name or message fields with a visible error
on success, show a confirmation page
Do not use any package outside Flask and the Python standard library

we dont need to store any data at the moment

 
## Scores
| Criterion | ChatGPT | Gemini | Claude |
|---|---|---|---|
| Correctness |5|5|4|
| Code quality | | | |
| Completeness |5|5|5|
| Security | | | |
 
## What each got wrong
Chat GPT - Nothing went wrong it ran perfectly apart from that I needed to add /contact to the end of the link everytime in order to open the web page but I think this is normal.
Gemini -Same. thing with the /contact. Also it forgot to create the "contact_success.html" and "contact.html" folders in the templates folder so the code didn't run correctly first time and we had to troubleshoot this.
Claude - Process was more convoluted. It made install a python extension when the other tools didn't. It gave me an app.py package to download but the steps it gave to run it weren't as simple as other tools. Contact form was very basic.
 
## Which I kept, and why
I could have picked either Chat GPT or Gemini but I'm going to pick to Gemini. It gave me an easy to understand step by step guide on how to run the contact form and the resulting contact form looked nice and comeplete. It also displayed a nice preview of the contact form in the chat before I ran it on my own computer. The form worked perfectly and didn't break when I enetered incorrectly formatted email or left the fields blank. It just displayed the warning message as expected. Chat GPT was the same and didn't give me any trouble but I'm sticking with Gemini. I couldn't break any of the contact forms by inputting incorrect information.