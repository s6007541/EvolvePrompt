sudo apt install openjdk-11-jdk-headless
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-1-openjdk-amd64/bin/java 11
sudo update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java
sudo update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-1-openjdk-amd64/bin/javac 11
sudo update-alternatives --set javac /usr/lib/jvm/java-11-openjdk-amd64/bin/javac
