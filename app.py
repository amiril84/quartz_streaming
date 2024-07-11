from flask import Flask, render_template, request, redirect, url_for, Response
import asyncio
from search import transform, search, answer, decide, complete
# Import necessary functions from the provided backend code

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Display the homepage with the search form
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search_results():
    if request.method == 'POST':
        user_query = request.get_json()['query']
        # Use the provided backend code to process the query and get results
        decision = decide(user_query)
        if decision == "search":
            new_queries = transform(user_query)
            snippets = asyncio.run(search(new_queries))
            response = answer(user_query, snippets)
        else:
            response = complete(user_query)
        def generate_stream():
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        return Response(generate_stream(), content_type='text/plain')
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)