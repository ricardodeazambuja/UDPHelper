# UDPHelper
## Very simple Python**3** library to send/receive variable length Numpy arrays

IMPORTANT: this library is hardcoded to format things as floats and it will not break the packet if it's bigger than the [machine's buffersize](http://man7.org/linux/man-pages/man7/socket.7.html):
```
$ cat /proc/sys/net/core/rmem_max  # on the receiver
```

```
$ cat /proc/sys/net/core/wmem_max  # on the sender 
```

You were warned ;)
