# What is this?

It's a simple API, plus a lot of scaffolding to get it to production at high performance with a smallish (~128MB dockerized) footprint.

Overall architecture is An API written in Flask, running on GUnicorn, behind nginx. Sqlite is used for persistent storage and Redis for caching.

Implementation is currently as one docker container running all the above services in an Alpine Linux environment. This container runs on AWS ECS with an EFS volume for persistent storage and a Network ELB for a static IP to the outside world. 

It's not difficult to break this up into separate containers for the nginx proxy, GUnicorn API workers, and Redis cahce, (and maybe add a real db while we're add it) - but that balloons the service footprint and introduces all kinds of container networking complexity. Docker Swarm or Kubernetes could be used as well, but Istuck to what I knew best in the interest of time.

# TODO

- Set up async job for cache warming
- Set up async job for purging old data from db
- Add caching for collect and monthly_uniques endpoints
- Tune Redis configuration
- More test cases
- E2E load testing
- HTTPS support
- Kubernetes instead of ECS?
- Architecture diagram