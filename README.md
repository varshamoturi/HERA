

# HERA: Where Connections Blossom and Memories Flourish

## Overview

HERA is more than a dating app; she's your friend, guide, and matchmaker. With advanced AI, HERA crafts personalized matches and unforgettable experiences tailored to your interests. In a world craving genuine connections, HERA revolutionizes how we bond and find love. Welcome to HERA – where meaningful connections feel effortless.

## Usage

To access the login page, open (https://hera-421105.uw.r.appspot.com) in your web browser.

## Installation

To run HERA locally, follow these steps:

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. generate your requirements:
   ```bash
    npm list --depth=0 --parseable | grep node_modules | sed 's/.*node_modules\///' > requirements.txt
    ```
4. Install requirements.txt
5. Start the server:

```bash
node server.js
```


## Files

The important files from repository:

- **public**: Contains HTML files for login and signup.
  - **login.html**: HTML file for the login page.
  - **signup.html**: HTML file for the signup page.
- **data_gen.py**: This script initiates the process by utilizing the OpenAI GPT-3.5 turbo model with prompt engineering. It generates five activities for any two users who have signed up in the app and become friends.
- **google_req.py**: After generating activities, this script handles the conversion of these activities into listings from Google Maps. It interacts with the Google Maps API to fetch relevant listings based on the generated activities.
- **listings.py**: This script acts as a pipeline between the data generation and Google Maps listing conversion processes. It accumulates the results and orchestrates the flow between different files. Finally, it provides the activities in JSON format, ready for further processing or presentation.

- **server.js**: serves backend logic for web application.



