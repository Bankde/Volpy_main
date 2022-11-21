// Define "global" variables
var serverIP = window.location.hostname;

// Signalling Variables (used to communicate via server)
var uuid;
var id;
var serverConnection;

var peerConnectionConfig = {
  'iceServers': [
    { 'urls': 'stun:stun.stunprotocol.org:3478' },
    { 'urls': 'stun:stun.l.google.com:19302' },
  ]
};

const MsgType = {
    INIT: 0,

    WS_DATA: 11,                   // For websocket data
    WS_HEARTBEAT_REQ: 12,          // For driver-node heartbeat
    WS_HEARTBEAT_RES: 13,

    SDP_OFFER: 21,
    SDP_ANSWER: 22,
    ICE_CANDIDATE: 23,
    WEBRTC_DATA: 24,               // P2P data
    WEBRTC_HEARTBEAT_REQ: 25,      // P2P heartbeat
    WEBRTC_HEARTBEAT_RES: 26
}

/*
The UUID will be used to establish the webRTC connection.
The ID will be used to decide by driver (master node) for which nodes is the caller.
    The higher ID (come later) will be the caller.
    We design this way so connecting to all the existing nodes can be done within the new node.

The webRTC connection can be divided into 3 steps:
1. Websocket establishment
    Connect with main server, get information about other cluster nodes.
2. WebRTC establishment
    At receiving other nodes' information:
      For every node id that's lower than us:
        - Create peerConnection for that node
        - Create datachannel
        - Send offer through the websocket server
      For every node id that's higher than us:
        - Create peerConnection for that node
        - Listen for the offer from the websocket server
        - Listen for the datachannel

The websocket data [node->driver] will be
{
  "uuid":
    // This node UUID, a node creates it.
}

The websocket data [driver->node] will be
{
  "uuid":
    // This node UUID, a node creates it.
  "id":
    // This node ID, a webserver assigns to a node.
  "list":
    // List of the cluster nodes
    [
      "target":
        // Target node to connect to
      "targetId":
        // Target node ID
    ]
}

The peerConnectionList data will be
{
  "uuid": 
    // UUID of the target
    {
      "webRTCEnable":
        // Boolean True/False
      "webRTC":
        "peerConnection":
          // The webRTC connection
        "dataChannel":
          // The webRTC datachannel
        "id":
          // ID of the target
        "state"
          // State of the connection
    }
}
*/

// RTC Variables!!
var peerConnectionList = {};

// Set things up, connect event listeners, etc.

function wss_send(msg, ) {
  return serverConnection.send(msg);
}

function startup() {
  // Set up connection to our websocket signalling server
  uuid = createUUID();
  serverConnection = new WebSocket('wss://' + serverIP + ':8443');
  serverConnection.onmessage = gotMessageFromServer;
  // Init websocket
  data = {
    'MsgType': MsgType.INIT,
    'uuid': uuid
  }
  wss_send(JSON.stringify(data))
    .then(() => console.log('Init node connection'))
    .catch(errorHandler);
}

// Handle messages from the Websocket signalling server

function gotMessageFromServer(event) {
  let data = JSON.parse(event.data);
  switch (data.MsgType) {
    case MsgType.INIT:
      // Save id and start the WebRTC handshake
      console.log('Recv node init, init webRTC and create sdp offer')
      id = data["id"]
      webRTC_init(true);
      data = {
        'MsgType': MsgType.SDP_OFFER,
        'sdp': peerConnection.localDescription, 
        'uuid': uuid
      };
      peerConnection.createOffer()
        .then(offer => peerConnection.setLocalDescription(offer))
        .then(() => wss_send(JSON.stringify(data)))
        .catch(errorHandler);
      break;
    case MsgType.SDP_OFFER:
      // Receive SDP Offer, initiate webRTC
      console.log('Recv sdp offer, init webRTC and create sdp ans')
      webRTC_init(false);
      data = {
        'MsgType': MsgType.SDP_ANSWER,
        'sdp': peerConnection.localDescription,
        'uuid': uuid
      };
      peerConnection.setRemoteDescription(new RTCSessionDescription(signal.sdp))
        .then(function () {
        peerConnection.createAnswer()
          .then(answer => peerConnection.setLocalDescription(answer))
          .then(() => wss_send(JSON.stringify(data)))
          .catch(errorHandler);
      });
      break;
    case MsgType.SDP_ANSWER:
      console.log('Recv sdp ans, init webRTC and create sdp ans')
      peerConnection.setRemoteDescription(new RTCSessionDescription(signal.sdp));
      break;
    case MsgType.ICE_CANDIDATE:
      console.log('received ice candidate from remote');
      peerConnection.addIceCandidate(new RTCIceCandidate(signal.ice))
        .then(() => console.log('added ice candidate'))
        .catch(errorHandler);
      break;

    case MsgType.WS_DATA:
    case MsgType.WEBRTC_DATA:
      break;

    case MsgType.WEBRTC_HEARTBEAT_REQ:
      break;
    case MsgType.WEBRTC_HEARTBEAT_RES:
      break;
    
    default:
      errorHandler("Unknown message: " + data);
  }
}

// Start the WebRTC Connection
// We're either the caller (when we click 'connect' on our page)
// Or the receiver (when the other page clicks 'connect' and we recieve a signalling message through the websocket server)

function webRTC_init(isCaller) {
  peerConnection = new RTCPeerConnection(peerConnectionConfig);
  peerConnection.onicecandidate = gotIceCandidate;

  // If we're the caller, we create the Data Channel
  // Otherwise, it opens for us and we receive an event as soon as the peerConnection opens
  if (isCaller) {
    dataChannel = peerConnection.createDataChannel("testChannel");
    dataChannel.onmessage = handleDataChannelReceiveMessage;
    dataChannel.onopen = handleDataChannelStatusChange;
    dataChannel.onclose = handleDataChannelStatusChange;
  } else {
    peerConnection.ondatachannel = handleDataChannelCreated;
  }
}

function gotIceCandidate(event) {
  if (event.candidate != null) {
    console.log('got ice candidate');
    serverConnection.send(JSON.stringify({ 'ice': event.candidate, 'uuid': uuid }))
    console.log('sent ice candiate to remote');
  }
}

// Called when we are not the caller (ie we are the receiver)
// and the data channel has been opened
function handleDataChannelCreated(event) {
  console.log('dataChannel opened');

  dataChannel = event.channel;
  dataChannel.onmessage = handleDataChannelReceiveMessage;
  dataChannel.onopen = handleDataChannelStatusChange;
  dataChannel.onclose = handleDataChannelStatusChange;
}

// Handles clicks on the "Send" button by transmitting

// a message to the remote peer.

function sendMessageThroughDataChannel(message) {
  message = "|" + message + "," + (new Date()).getTime() + "|";
  console.log("sending: " + message);
  dataChannel.send(message);
}

// Handle status changes on the local end of the data
// channel; this is the end doing the sending of data
// in this example.

function handleDataChannelStatusChange(event) {
  if (dataChannel) {
    console.log("dataChannel status: " + dataChannel.readyState);
    if (dataChannel.readyState == "open") globalState = true;
    else globalState = false;
  }
}

// Handle onmessage events for the data channel.
// These are the data messages sent by the remote channel.

function handleDataChannelReceiveMessage(event) {
  console.log("Recv: |" + event.data + "," + (new Date()).getTime() + "|");
  if (event.data.startsWith("|start")) {
    sendMessageThroughDataChannel(event.data);
  }
}

// Close the connection, including data channels if it's open.
// Also update the UI to reflect the disconnected status.

function disconnectPeers() {

  // Close the RTCDataChannel if it's open.

  dataChannel.close();

  // Close the RTCPeerConnection

  peerConnection.close();

  dataChannel = null;
  peerConnection = null;
}

function errorHandler(error) {
  console.log(error);
}

// Taken from http://stackoverflow.com/a/105074/515584
// Strictly speaking, it's not a real UUID, but it gets the job done here
function createUUID() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
  }

  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

function repeatMessage() {
    if (globalState == false) return;
    sendMessageThroughDataChannel("start");
}

const sleep = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms))
}

async function main() {
    startup();
    await sleep(5000);
    connect();
    setInterval(repeatMessage, 5000); 
}
main();