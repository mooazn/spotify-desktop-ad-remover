# Deal with Spotify Ads

## Should be run with administrator privileges for best results. Everytime that I mention Spotify, assume that I am referring to the free version.

_Really simple application that reopens the Spotify Desktop Application when ads start to play. This only works on Windows and the free version of Spotify. No reason to use this if you have premium anyway..._ 

This project started out as a simple idea to skip ads when I'm listening to Spotify. Ads will always be annoying but that's why there's things like ad blocker out there. What about when an ad is playing on a desktop application (like Spotify)? My idea here was to create something that could easily skip ads without me doing anything. I have been using desktop Spotify for a couple of years now and something I've done to skip ads is to simply close and reopen the Spotify desktop application. This resets the state of Spotify and you continue playing the next song without having to hear the ad. All I wanted to do is automate this process. Thus, this application was made. Let's look closer at how this works:

1. The code opens up a selenium-based Chrome browser (you have to have the chromedriver)
2. The browser navigates to Spotify.com
3. The browser clicks on the "Log in" button
4. The browser clicks on the "Continue With Facebook" button *
5. The browser logs into the linked Facebook account for the user with the correct credentials
6. The browser navigates to the developer API (specifically, https://developer.spotify.com/console/get-users-currently-playing-track/)
7. The browser clicks "Get Token" and selects the "user-read-currently-playing" scope
8. The browser then clicks "Request Token"
9. We store the time that we got the token
10. Since the user is logged in, the value in the OAuth Token field is the user's OAuth Token
11. The browser stops doing stuff (but continues to stay there). You can think of it as the browser sleeping on the webpage **
12. The code hits the API endpoint (https://api.spotify.com/v1/me/player/currently-playing) with the appropriate headers (one of them is the OAuth Token)
13. We get "currently_playing_type" from the JSON data and if it is != "track", we continue to 14. If it is == "track", go to 12 ***
14. We close Spotify and reopen it (we also skip the song if it was the same song playing before the ad occured) ****
15. We check if it's been 3500 seconds since we registered a new token. If it has, continue to 16. If not, go to 12
16. Go to step 6. This resets the token
17. Close and quit browser when user closes the program

_*_ = This was something that took some time to discover and understand. Spotify's login is extremely weird. I went through "hours" of trouble trying to login to Spotify through Selenium only to be met with some sort of error. Sometimes, this error did not occur. However, it had become a prominent issue and it was annoying since the program kept crashing since logging in was not working. At one point, I thought I had found a hack where I could go back to the login page after doing something and login. This worked for a while but broke as well for some reason. Whatever, logging in through Facebook is the easiest option. Unfortunately, this requires that your Spotify is linked to a Facebook account. However, I believe that even making a dummy account and linking it should be good enough.

** = The browser does not close everything. I wanted it to stay in one place without having to worry about logging in again and again (as that would be time consuming). Thus, I have it stay on the API page while the program runs. This way I do not have to worry about logging in (that's only a one time issue). I'm also assuming that Spotify won't automatically log you out after 24 hours or something. Who listens to Spotify that long anyway...

*** = You can add more checks here. I am assuming that everything other than a track is something I do not want. Ads fall into this category, but so do episodes/shows on Spotify. If you don't want the program to skip those, then you have to add those checks in. All I wanted for myself was to skip anything other than a track.

**** = We store the song ID of whatever was playing when we hit the API. Once an ad is encountered and we reopen Spotify, we check if the new Song ID is the same as the one that was playing before the ad (this is because the API finds out that an ad is playing faster than it actually plays it if timed correctly). If the two songs IDs are the same, we simply skip the current song ID because it is a repeat. We assume that the next song is not the same as the current one. Even if it was, no big deal. The funny thing about Spotify is that if you play the same song over and over (you have it on repeat current track), then you will never ever get an ad. 

2 things...

**I created a really simple batch script which runs the program in the background and has the selenium-based browser as headless. Check out the script for more information.** 

**Although I have tried to implement error handling as best as possible, this program sometimes crashes for "some" reason.**

Simple Workflow (assuming you do not have batch script):

1. Run the code. Make sure you have all libraries installed, the chromedriver, the correct location of Spotify, and the correct credentials for Facebook
2. Open Spotify and start listening

Simple Workflow (assuming you have the batch script):

1. Make sure you have all libraries installed, the chromedriver, the correct location of Spotify, and the correct credentials for Facebook. 
2. Run the batch file.
3. Start listening on Spotify (the batch file opens Spotify for you)

