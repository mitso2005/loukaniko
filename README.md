- [**API Root**](https://loukaniko-api.onrender.com/)
- [**Interactive Docs (Swagger)**](https://loukaniko-api.onrender.com/docs)
- [**ReDoc**](https://loukaniko-api.onrender.com/redoc)

#Limitations
- Only works for ~80 differnet countries due to the limited free fx rates I have access to.
- get_travel_value_index_ranked is quite slow due to limited caching of historical data.

Will improve on these limitations by:
- Upgrading to use [hexarate.paikama.co](https://hexarate.paikama.co/) for daily fx data for over 170 currencies
- Getting better SQL skills
