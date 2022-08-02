WebRTC Example - RTCDataChannel
==============

This is a fork of Shane Tully's (shanetully.com)  original 'as simple as it gets' WebRTC Example.  
https://github.com/shanet/WebRTC-Example

As the name suggests, the aim of this fork is to use an RTCDataChannel instead of the normal media track.

The RTCDataChannel specific code is based on Mozilla's RTCDataChannel sample:  
https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Simple_RTCDataChannel_sample

Note that as per the original repo, this project uses a Websocket as the signalling server.  
The node.js server sets up a Websocket, and each 'client' connects to it with a unique UUID.  
The server then broadcasts out every message that it receives, and the clients then decide what to do with each message
(and ignore it if it actually originally came from them!)

The following instructions are a slightly modified version of those (still relevant) in the main repo:

## Usage

The signaling server uses Node.js, `express` and `ws` and can be started as such:

```
$ npm install
$ npm start
```

With the server running, open two windows of a recent version of Firefox, Chrome, or Safari and visit `https://localhost:8443`.

* Note the HTTPS! There is no redirect from HTTP to HTTPS.
* Some browsers or OSs may not allow the webcam to be used by multiple pages at once. You may need to use two different browsers or machines.

## TLS

Recent versions of Chrome require secure websockets for WebRTC. Thus, this example utilizes HTTPS. Included is a self-signed certificate that must be accepted in the browser for the example to work.

## Problems?

WebRTC is a rapidly evolving beast. Being an example that I don't check often, I rely on users for reports if something breaks. Issues and pull requests are greatly appreciated.

## License

The MIT License (MIT)

Copyright (c) 2019 Shane Tully, Zac Duthie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
