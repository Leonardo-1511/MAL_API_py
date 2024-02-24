# MAL API py
## About
This is supposed to become an API wrapper of sorts for [MyAnimeList](https://myanimelist.net). You can see the documentation for the API [here](https://myanimelist.net/apiconfig/references/api/v2).

Currently the Oauth2 flow is working, but it is all still manual. This means that you need to call the functions one after another in sequence to get the Access Token and so on.

> [!NOTE]
> You can expect a automatic flow with Client classes and a complete wrapper for the current endpoints on the MAL docs within the comming weeks.


## To-do
- MAL endpoints
  - [ ] Anime
  - [ ] User Animelist
  - [ ] Forum
  - [ ] Manga
  - [ ] User Mangalist
  - [ ] User
- Authorization
  - [x] Oauth2 flow
  - [x] Client ID headers (for Public access)
  - [ ] Automatic Access Token retrieval (Client class?)
  - [ ] Secure Token saving
