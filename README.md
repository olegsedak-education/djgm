# DjangoGramm Full Setup

DjangoGramm is a social web application inspired by Instagram. It allows users to register, create profiles, share posts
with multiple images, follow other users, and interact through likes. The application emphasizes privacy by restricting
access to user profiles and images to authorized users only.

## Project Overview

- **User Registration and Confirmation**  
  Users register using their email address. After initial registration, a confirmation email with a unique link is sent
  to verify the account. Upon confirmation, the user is redirected to their profile page to complete their information
  by adding their full name, bio, and avatar.

- **Posts and Media**  
  Users can create posts that contain multiple images. Each post can be tagged with multiple tags, and users are able to
  add new tags as authors. Posts appear in a feed sorted by the latest activity.

- **Social Interactions**  
  Users can follow and unfollow other users. Each user has a personalized news feed displaying recent posts from those
  they follow. Additionally, users can like and unlike posts.

- **Access Control**  
  Profiles and posts are private to authorized users; guests or unauthorized users cannot view profiles or images.

- **Frontend and Design**  
  The UI is built using Bootstrap to provide a clean and responsive design.

## Third-Party Services

- **Cloudinary**  
  Used for secure and scalable storage of images and videos. This allows handling of multiple images per post
  efficiently and ensures fast delivery through a CDN.  
  [Cloudinary Documentation for Django](https://cloudinary.com/documentation/django_image_and_video_upload)

- **Mailjet**  
  Used for sending confirmation emails and other email notifications reliably with tracking and analytics features.

## Getting Started

You can try this project yourself by cloning this repository and following the deployment instructions in
the [PRODUCTION.md](./PRODUCTION.md) file. The PRODUCTION guide covers:

- Preparing a clean server environment
- Configuring environment variables securely
- Running initialization and installation scripts
- Setting up Gunicorn, Nginx, and systemd services
- Deploying the Django application in production mode

---

This repository contains the full Django project source code along with all infrastructure files and deployment scripts
necessary for setting up the application on a fresh server.

---

## Testing

The project includes unit tests using the `unittest` module and/or `pytest` to ensure code quality and functionality.

---

Feel free to explore the project, test its features, and contribute improvements!

## License

This project is licensed under the [MIT License](LICENSE).