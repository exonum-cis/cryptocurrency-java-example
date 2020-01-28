# Cryptocurrency Demo

This project demonstrates how to bootstrap your own cryptocurrency with Exonum CIS Java Bindings.

Exonum blockchain keeps balances of users and handles secure
transactions between them.

It implements most basic operations:

- Create a new user
- Transfer funds between users

## Install and Run

### Manually

#### Getting Started

Be sure you installed necessary packages:
- Linux or macOS. 
- Exonum CIS Java
- [JDK 1.8+](http://jdk.java.net/12/).
- [Maven 3.5+](https://maven.apache.org/download.cgi).
- [git](https://git-scm.com/downloads)
- [Node.js with npm](https://nodejs.org/en/download/)
- [Exonum Launcher][exonum-launcher] python application.
- Exonum Launcher Java Plugins.

#### Build and Run

Build the service project:

```sh
$ mvn install 
```

Start the node:
```sh
$ ./start-node.sh
```

Start the service:
```sh
$ python3 -m exonum_launcher -i cryptocurrency-demo.yml
```

---