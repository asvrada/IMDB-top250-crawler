import json

# data = None

with open('./scrapy_version/IMDBTop/data.json') as json_data:
    data = json.load(json_data)
    data = sorted(data, key=lambda x: x["imdb_rank"])

with open('./scrapy_version/IMDBTop/data.json', 'w') as outfile:
    json.dump(data, outfile)
