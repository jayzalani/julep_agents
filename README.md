# Dining Places Finder Agent

This Agent will help you find dining places around cities with just 3 clicks! You don't have to do the extra hard work of getting addresses, dining types, and figuring out what each city's flavor is - this will help you out with all of that.

## How to use it

Just install dependencies mentioned in requirements.txt. For now there are my API keys (YES I KNOW! THEY ARE THERE INTENTIONALLY) - will remove them in the meantime, so you're good to go. Don't forget to install env first since the project is in Python and we should follow best practices:

```bash
python main.py
```
or
```bash
python app.py
```

## Difference between the files

Both files serve the same purpose but main.py is different from app.py in some context. When you need to get a smart report that can be useful in offline settings, this code generates a .pdf file after execution. Please go to the `foodie_tours_pdf` folder for example usage.

The app.py file is the CLI program where you can check the response in raw JSON format and use it wherever you want - in applications or chatbots as we wish.

I used Julep in the backend and their APIs are pretty useful for making this particular project and for creating agents. Feel free to check it out!

For Julep, I initially tried to make an agent that could directly send PDFs to email using the Email.yaml file, but it didn't work properly in my case (I think I need to implement it more precisely). It was taking a very long time - like 30 minutes - and still no email was sent.

In the end, it was fun! I enjoyed making this project. Being honest, I took help from Claude for PDF formatting purposes because that's just a styling thing. Hope you understand 😅

## Architecture 

This follows the simple architecture mentioned in Julep AI documentation where you simply make a .yaml file for tasks and agents, then create driver code that starts the application and uses this .yaml file to execute the agent.
