## Instructions:

1. Clone the repo to the pi.

```
git clone https://github.com/WiIIiamTang/fsauthed-service.git
cd fsauthed-service
pip3 install Flask requests
```

2. Get the `key.json` file from admin and put it in the root directory of the repo.

```
$ ls
drop1/  key.json  pi/  README.md
```

3.

```
$ pwd
<copy_this_path>
```

4. Run the crontab command to edit the crontab file.

```
crontab -e
```

- There could be a message that says "no crontab for user - using an empty one". Select vim and continue.

5. Add the following lines to the crontab file. Use the path you copied in step 3 to fill in the abspath.

```
@reboot python3 <abspath_to_repo>/pi/boot.py -k <abspath_to_key.json> --root <abspath_to_repo> &
0 1 * * * python3 <abspath_to_repo>/pi/job.py -k <abspath_to_key.json> --root <abspath_to_repo>
```

6. Save and exit the crontab file.

```
:wq
```

7. Check that the crontab file is correct.

```
crontab -l
```

8. (Optional) Reboot

```
sudo reboot
```
