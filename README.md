# Connect-k

Flask-based Python web-game, hosted with Google App Engine, called `Connect-k`:
a 2-player game where players take turns placing pieces onto the bottom row of
an infinite grid. The game ends if a player's pieces form a contiguous line
(horizontal or vertical) of length `k`.
Try it out [here](https://connect-k-356300.ue.r.appspot.com/).
<a href="https://connect-k-356300.ue.r.appspot.com/">
  <img src="https://github.com/mrowan137/connect-k/blob/main/docs/demo/connect-k-demo.gif">
</a>


## Description

Supported gameplay options:
  * Value of `k`: length of the line required to win
  * Player color: red or blue
  * Player to go first: red or blue
  * Opponent: computer (easy), computer (hard), human


## Dependencies

  * [Flask](https://github.com/pallets/flask)
    * [Werkzeug](https://palletsprojects.com/p/werkzeug/)
    * [Jinja](https://palletsprojects.com/p/jinja/)
    * [MarkupSafe](https://palletsprojects.com/p/markupsafe/)
    * [ItsDangerous](https://palletsprojects.com/p/itsdangerous/)
    * [Click](https://palletsprojects.com/p/click/)
  * [WTForms](https://github.com/wtforms/wtforms)
  * [uuid](https://docs.python.org/3/library/uuid.html)


## Help

  * If multiple web browser tabs are open and identified as belonging to the
  same user, be aware that it modifies the same game data; opening, for example,
  another tab in the same web browser could be identified as belonging to the
  same user. On the other hand, accessing another game session from a new
  'incognito' window could be identified as belonging to a separate user and
  would generate separate game data.

## Useful Google Cloud App Engine commands

This application is hosted using Google App Engine (there are great tutorials
for how to deploy a Flask app using App Engine, e.g.
[this tutorial](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab)).
When working with the App Engine platform, the following are some useful
`gcloud` commands:
  * Deploy changes to the Google App Engine server:
  `gcloud app deploy`.
  * Open the most recent app version in a web browser:
  `gcloud app browse`.
  * List all versions deployed to App Engine server:
  `gcloud app versions list`.
  * There's a limit to how many versions of the app you can store on App Engine;
  if you have too many you will not be able to upload more unless deleting some
  old ones. There is a useful script [here](https://almcc.me/blog/2017/05/04/removing-older-versions-on-google-app-engine/)
  that can remove all but the `n` most recent versions.  With `n`=2, it could be
  called like this to delete all but the 2 most recent versions:
  `sh delete-older-gcloud-app-versions.sh default 2`.
  After doing this, you can deploy the most recent version of the app.
  

## Author

Michael E. Rowan — [mrowan137](https://github.com/mrowan137) — [michael@mrowan137.dev](mailto:michael@mrowan137.dev).


## License

[MIT License](https://github.com/mrowan137/connect-k/LICENSE).


## Acknowledgments

  * [Flask](https://palletsprojects.com/p/flask/)
  * [WTForms](https://wtforms.readthedocs.io/en/3.0.x/)
  * [Google Cloud App Engine](https://cloud.google.com/appengine)
  * [Google Cloud App Engine: how to remove older versions?](https://almcc.me/blog/2017/05/04/removing-older-versions-on-google-app-engine/)
  * [Google Cloud App Engine: useful script for removing older versions](https://gist.github.com/spark2ignite/75613f590a24244356472b1e06eac4df)
  * [Tutorial: deploying a Flask app to Google App Engine](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab)
  * [easyAI TicTacToe](https://github.com/Zulko/easyAI/blob/master/easyAI/games/TicTacToe-Flask.py)
  * [CSS glowing border](https://stackoverflow.com/questions/5670879/css-html-create-a-glowing-border-around-an-input-field)
  * [CSS button bigger on hover](https://stackoverflow.com/questions/37357402/css-button-animation-getting-bigger)
  * [Press Start 2P font](https://fonts.google.com/specimen/Press+Start+2P/about?selection.family=Open+Sans&sidebar.open=)
