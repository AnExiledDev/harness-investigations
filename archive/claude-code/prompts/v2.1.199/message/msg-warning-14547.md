---
id: msg-warning-14547
name: Warning Message
category: message
subcategory: warning
source_line: 14547
---

),
          this.rejectPendingCalls(
            new XR("Bridge keepalive timeout \u2014 connection dead"),
          ),
          this.closeSocket(),
          this.scheduleReconnect());
    }, Idu);
  }
  stopKeepAlive() {
    if (this.keepAliveInterval)
      (clearInterval(this.keepAliveInterval), (this.keepAliveInterval = null));
    this.lastPongReceived = 0;
  }
  closeSocket() {
    if ((this.stopKeepAlive(), this.handshakeTimer))
      (clearTimeout(this.handshakeTimer), (this.handshakeTimer = null));
    if (this.ws) {
      if (
        (this.ws.removeAllListeners(),
        this.ws.on("error", () => {}),
        this.ws.readyState === $ye.default.OPEN)
      )
        this.ws.close();
      else this.ws.terminate();
      this.ws = null;
    }
    if (
      ((this.connected = !1), (this.authenticated = !1), this.selectedDeviceId)
    )
      this.previousSelectedDeviceId = this.selectedDeviceId;
    if (
      ((this.selectedDeviceId = void 0),
      (this.discoveryComplete = !1),
      (this.multiBrowserPendingSelection = !1),
      (this.pendingPairingRequestId = void 0),
      (this.pairingInProgress = !1),
      this.abortPairingPrompt(),
      this.pendingSwitchResolve)
    )
      (this.pendingSwitchResolve(null), (this.pendingSwitchResolve = null));
    if (this.pendingDiscovery)
      (clearTimeout(this.pendingDiscovery.timeout),
        this.pendingDiscovery.resolve([]),
        (this.pendingDiscovery = null));
    if (this.peerConnectedWaiters.length > 0) {
      let e = this.peerConnectedWaiters;
      this.peerConnectedWaiters = [];
      for (let t of e) t(!1);
    }
  }
  rejectPendingCalls(e) {
    for (let t of this.pendingCalls.values())
      (clearTimeout(t.timer), t.reject(e));
    this.pendingCalls.clear();
  }
  cleanup() {
    if (this.reconnectTimer)
      (clearTimeout(this.reconnectTimer), (this.reconnectTimer = null));
    (this.rejectPendingCalls(new XR("Bridge client disconnected")),
      this.closeSocket(),
      (this.reconnectAttempts = 0));
  }
}
function Bdn(e) {
  return new Ndn(e);
}
var $ye,
  Idu = 30000,
  Whs = 90000,
  qhs = 30000;
var ixr = E(() => {
  dtt();
  $ye = D(require("ws"));
});
function JRt(e) {
  return (
    
