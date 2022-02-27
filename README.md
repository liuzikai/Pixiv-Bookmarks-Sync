# Pixiv Bookmarks Sync
A utility to incrementally sync personal (or other user's) Pixiv illustration bookmarks to sqlite db and original images to local.

## Dependencies
* [PyPixiv](https://github.com/Yukariin/PyPixiv)
* termcolor

## Usage
* Download files
* Install dependencies
```shell
pip install -r requirements.txt
```
* Change `_USERID` in `pixiv_collection_main.py` to the Pixiv user ID you want to sync. Change `_USESNI`, `_USERNAME`, `_PASSWORD` and interval parameters above as needed.
* To run once, use
```shell
python pixiv_collection_main.py
```
* To deploy it in `screen`, etc. to run daily (on a server, for example), use
```shell
python platform_module.py
```
You can type `help` when program runs.

## Miscellaneous
* Remember to respect the original author. Don't use image without authorization or proper citations.
* The synchronization is incremental, which means database entry and illustration(s) of a deleted bookmark won't be deleted.
* Also, we assume that ALL new bookmarks are before ALL recorded bookmarks (which is the natual behavior of Pixiv). But if you unmark A, mark B and C, and then remark A, B and C will be missed since the program encounter A and assume that all later bookmarks have been recorded. You can comment the if block at about line 43 to disable this feature.
* Illustration images will only be download once. Moving, renaming or deleting local image files won't result in redownloading.
* Frequent requests to Pixiv may result in blocking of IP. Use at your own risk.
* To decrease the frequency of web requesting, several intervals are set between requests of webpages or illustrations, such as `_SYNCINTERVAL`, `_DOWNLOADINTERVAL` and `_RETRYINTERVAL`. See comments in `pixiv_collection_main.py`. Change it as you need.
* If it takes long to download images, you may want to put it into background using `screen`, etc.
