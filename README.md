## Task 13 Add extended functionality to DjangoGramm application

#### The application describes by STORYLINE from previous task (Task 11 Decompose project)

#### Storyline from Task 11
Write a program like Instagram. This application must have a web interface. The user can register on the website by email. After basic registration, the user will receive a confirmation of the continuation of registration. The email must have a unique link. The user who goes by a link should be redirected to the profile page and add his full name, bio, and avatar. Next, the user can use DjangoGramm.
He can create posts with images, looks posts of other users via a feed of the latest posts. Unauthorized guests cannot view the profile and pictures of users.
Additional functional requirements (added 20.01.2022 by Vadym Serdiuk):
- Each post may have multiple images
- Each post may have multiple tags. New tags may be added by authors.
- Users may like posts (and unlike as well)



### Modify the application to add new functionality. User can subscribe to other users. The user has a news feed where he watches recent events. Friends (the users I'm subscribed to) post images and subscribe or unsubscribe to other users. Users can put likes/unlike pictures of other users.
  

### The plan:

1. Use bootstrap to make a pretty view, etc.
2. Add following and follower entity.
3. Add likes entity.
4. Use a third-party service for storing images.
5. Deploy the code to the server.

#### Resources:

Cloudinary https://cloudinary.com/documentation/django_image_and_video_upload

Write tests using Unittest module or py.test.