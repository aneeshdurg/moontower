class PictoChat {
  draw = false;
  lock = false;
  last_x = 0;
  last_y = 0;

  constructor(canvas, send_btn, chatroom) {
    this.canvas = canvas;
    this.chatroom = chatroom;
    this.ctx = canvas.getContext("2d");

    const start_drawing = (event) => {
      event.preventDefault();
      if (this.lock) {
        return;
      }
      this.draw = true;
      this.last_x = -1;
      this.last_y = -1;
    }
    this.canvas.addEventListener("touchstart", start_drawing);
    this.canvas.addEventListener("mousedown", start_drawing);

    const stop_drawing = (e) => {
      e.preventDefault();
      this.draw = false;
    };
    canvas.addEventListener("touchcancel", stop_drawing);
    canvas.addEventListener("touchend", stop_drawing);
    canvas.addEventListener("mouseup", stop_drawing);

    const drawmove = (event) => {
      event.preventDefault();
      if (this.draw) {
        const coords = this.getCoordsFromEvent(event, canvas);
        const x = coords.x;
        const y = coords.y;
        if (this.last_x < 0) {
          this.last_x = x;
          this.last_y = y;
        }

        this.ctx.beginPath();
        this.ctx.moveTo(this.last_x, this.last_y);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();

        this.last_x = x;
        this.last_y = y;
      }
    }
    canvas.addEventListener("mousemove", drawmove);
    canvas.addEventListener("touchmove", drawmove);

    send_btn.addEventListener("click", async () => {
      this.draw = false;
      this.lock = true;
      send_btn.disabled = true;
      const data = canvas.toDataURL();
      try {
        const resp = await fetch("/~aneesh/cgi-bin/chat/chat.py?send", {
          method: "POST",
          body: `img=${data}`,
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          }
        });
        console.log(resp);
        this.ctx.clearRect(0, 0, canvas.width, canvas.height);
      } catch (e) {
        // TODO - don't clear rect until success
        console.log("ERROR sending");
        console.log(e);
        // TODO use HTML modal instead
        alert("sending message failed :(");
      }
      send_btn.disabled = false;
      this.lock = false;
      console.log("sending?");
    });

    // Start listening to events from server
    this.listener();
  }

  getCoordsFromEvent(event, canvas) {
    const rect = canvas.getBoundingClientRect()
    const cx = event.clientX || event.targetTouches[0].clientX;
    const cy = event.clientY || event.targetTouches[0].clientY;
    const x = (cx - rect.left) / rect.width * canvas.width;
    const y = (cy - rect.top) / rect.height * canvas.height;

    return { x: x, y: y };
  }

  // Trigger deletion of old messages
  prune() {
    fetch("/~aneesh/cgi-bin/chat/chat.py?prune");
  }

  createDOMFromMessage(msg) {
    // messages are base64 encoded in the format `msg=<payload>`
    const message = atob(msg.message).trim().substring(4)

    const newElement = document.createElement("div");
    newElement.classList.add("msg");
    newElement.innerHTML += `<div class='msgtimestamp'>${msg.timestamp}</div>`;
    if (message.startsWith("data:image")) {
      newElement.innerHTML += `<img class="msgimg" src="${message}"></img>`;
    } else {
      // This is probably unused now, but useful for debugging
      newElement.innerHTML += `<div class='msgcontent'>${message}</div>`;
    }
    newElement.innerHTML += `<br>`;
    return newElement;
  }

  last_ts = "1970-01-01+00:00:00.00"
  prune_counter = 0;

  listener() {
    const evtSource = new EventSource(`/~aneesh/cgi-bin/chat/chat.py?listen=${this.last_ts}`);
    evtSource.onopen = (_e) => { console.log("Opening source"); };
    evtSource.onmessage = (e) => {
      // TODO - have a max scrollback of `n` messages
      if (e.data == "heartbeat") {
        return;
      }

      const msg = JSON.parse(e.data);
      const newElement = this.createDOMFromMessage(msg);
      this.chatroom.appendChild(newElement);

      // Scroll down to the new message on a delay (without the delay it won't
      // have calculated scrollHeight yet and won't scroll
      setTimeout(() => { this.chatroom.scrollTop = this.chatroom.scrollHeight; }, 10);

      // If/when we drop the connection, knowing the last timestamp will allow us to create a new connection and only
      // request new messages
      this.last_ts = msg.timestamp.replaceAll(' ', '+');
    };
    evtSource.onerror = (_e) => {
      console.log("Closing source");
      evtSource.close();
      // Reopen the source
      this.listener();
      this.prune_counter += 1;
      if (this.prune_counter % 4 == 0) {
        this.prune();
        this.prune_counter = 0;
      }
    };
  }
}



document.addEventListener("DOMContentLoaded", async () => {
  const send = document.getElementById("send");
  const canvas = document.getElementById("mycanvas");
  const chatroom = document.getElementById("chatroom");
  const chatapp = new PictoChat(canvas, send, chatroom);
  // Make chatapp globally available for debugging
  window.chatapp = chatapp;
});
