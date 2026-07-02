---
id: msg-warning-14367
name: Warning Message
category: message
subcategory: warning
source_line: 14367
---

),
          this.rejectPendingCalls(
            new nR("Bridge keepalive timeout \u2014 connection dead"),
          ),
          this.closeSocket(),
          this.scheduleReconnect());
    }, rUc);
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
        this.ws.readyState === Hme.default.OPEN)
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
    (this.rejectPendingCalls(new nR("Bridge client disconnected")),
      this.closeSocket(),
      (this.reconnectAttempts = 0));
  }
}
function qnn(e) {
  return new Vnn(e);
}
var Hme,
  rUc = 30000,
  HJo = 90000,
  AJo = 30000;
var ghr = E(() => {
  g7e();
  Hme = L(require("ws"));
});
function Yvt(e) {
  return (
    
