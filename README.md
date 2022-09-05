# Linkedin Web Scraping
Using comma counting and pattern matching techniques, I am able to successfully webscrape linkedin companies and profiles in 2022/2023.

The issue I had with web scraping linkedin was how LinkedIn changed its UI, having every element inside its own CSS and div classes to prevent functions like find_all() 
from working. Yet, they still kept in the weird UI structures in a unordered list (ul tag) which I was able to search through and after getting the text from each element, you can decipher which text comes from which part of the profile (12 spaces for experience vs 7 spaces for awards/certifications) and then store it and output to a json.

**Note this is still being used for a paid research project, so I will release this repo in a more user friendly form in classes, but as of now, you will need to mess around with my code
