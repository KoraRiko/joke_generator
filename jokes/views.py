from django.shortcuts import render
from .models import Joke
from .forms import KeywordForm
import openai
from django.conf import settings

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def joke_generator(request):
    # Initialize the form and fetch jokes in reverse chronological order
    form = KeywordForm()
    jokes = Joke.objects.all().order_by('-timestamp')  # Display jokes in reverse chronological order

    # Handle form submission
    if request.method == "POST":
        form = KeywordForm(request.POST)
        if form.is_valid():
            # Get the keyword from the form
            keyword = form.cleaned_data['keyword']
            
            # Generate a joke using OpenAI ChatGPT API
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # You can update the model to a more recent version
                    messages=[ 
                        {"role": "system", "content": "You are a joke generator."},
                        {"role": "user", "content": f"Tell a joke about {keyword}. Make it original and creative."}
                    ],
                    temperature=0.7
                )
                joke_text = response.choices[0].message.content.strip()  # Correctly accessing the joke content
            except Exception as e:
                joke_text = "Sorry, I couldn't generate a joke at the moment. Please try again later."

            # Save the joke to the database
            new_joke = Joke.objects.create(keyword=keyword, joke=joke_text)
            
            # Get the most recent joke after saving it
            recent_joke = Joke.objects.latest('timestamp')  # Get the latest joke by timestamp

    # Always fetch jokes in reverse chronological order for display
    jokes = Joke.objects.all().order_by('-timestamp')  # Reload jokes after adding the new one

    # Render the template with the form and the list of jokes
    return render(request, 'joke_generator.html', {'form': form, 'jokes': jokes, 'recent_joke': recent_joke})
