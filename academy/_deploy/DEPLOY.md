# Deploying the academy

## 1. Upload
Copy this whole folder to your server, e.g. `/var/www/hiregen/academy/`.
Do not upload `_deploy/` — it is notes for you, not for the web.

## 2. Serve it
Add the block in `nginx-academy.conf` **above** your app's `location /`.
Nginx matches the more specific prefix first, but confirm rather than assume:
your app almost certainly has a catch-all route that would swallow /academy/.

## 3. robots.txt
Add the line in `robots-additions.txt` to the root robots.txt. A robots file
inside a subfolder does nothing.

## 4. Verify — all five should pass
- https://hiregen.com/academy/                                  -> course home
- https://hiregen.com/academy/module-4/lesson-4.html             -> a lesson
- https://hiregen.com/academy/assets/course.css                  -> CSS, not HTML
- https://hiregen.com/academy/sitemap.xml                        -> XML
- https://hiregen.com/academy/dataset/ai-recruitment-dataset.zip -> downloads

## 5. Search Console
Add the property, submit /academy/sitemap.xml, then check Enhancements for the
Course structured data.

## 6. Things to change before launch
- `SIGNUP_URL` in build.py, if /signup?ref=academy is not the real path.
- `UPDATED` / `UPDATED_ISO` in build.py on every content revision.
- Module 11 lesson 1 and Module 8 lesson 4 date fastest. Review quarterly.
