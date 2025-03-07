document.addEventListener("DOMContentLoaded", async () => {
  const msg = document.getElementById("msg");
  const send = document.getElementById("send");

  const chatroom = document.getElementById("chatroom");

  const canvas = document.getElementById("mycanvas");
  const ctx = canvas.getContext("2d");
  console.log(ctx);

  let draw = false;
  let last_x = 0;
  let last_y = 0;
  const start_drawing = (event) => {
    event.preventDefault();
    draw = true;

    const rect = canvas.getBoundingClientRect()
    const cx = event.clientX || event.targetTouches[0].clientX;
    const cy = event.clientY || event.targetTouches[0].clientY;
    const x = (cx - rect.left) / rect.width * canvas.width;
    const y = (cx - rect.top) / rect.height * canvas.height;
    console.log("touch down", x, y, event)
    console.log("  ", event.clientX, event.clientY)
    console.log("  ", rect.left, rect.top)
    console.log("  ", rect.width, rect.height)
    console.log("  ", canvas.width, canvas.height)

    last_x = -1;
    last_y = -1;
  }
  canvas.addEventListener("touchstart", start_drawing);
  canvas.addEventListener("mousedown", start_drawing);

  const stop_drawing = (e) => {
    e.preventDefault();
    draw = false;
  };
  canvas.addEventListener("touchcancel", stop_drawing);
  canvas.addEventListener("touchend", stop_drawing);
  canvas.addEventListener("mouseup", stop_drawing);

  const drawmove = (event) => {
    event.preventDefault();
    const rect = canvas.getBoundingClientRect()
    const cx = event.clientX || event.targetTouches[0].clientX;
    const cy = event.clientY || event.targetTouches[0].clientY;
    const x = (cx - rect.left) / rect.width * canvas.width;
    const y = (cy - rect.top) / rect.height * canvas.height;
    if (draw) {
      if (last_x < 0) {
        last_x = x;
        last_y = y;
      }
      ctx.beginPath();
      ctx.moveTo(last_x, last_y);
      ctx.lineTo(x, y);
      ctx.stroke();
      last_x = x;
      last_y = y;
    }
  }
  canvas.addEventListener("mousemove", drawmove);
  canvas.addEventListener("touchmove", drawmove);

  // const chatform = document.getElementById("chatform")
  // chatform.onsubmit = () => {
  //   console.log("submitted form?");
  // };
  send.addEventListener("click", async () => {
    const data = canvas.toDataURL();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    console.log("sending?");
    try {
      const resp = await fetch("/~aneesh/cgi-bin/chat/chat.py?send", {
        method: "POST",
        body: `img=${data}`,
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        }
      });
      console.log(resp);
    } catch (e) {
      console.log("ERROR");
      console.log(e);
    }
  });

  // Trigger deletion of old messages
  const prune = () => {
    fetch("/~aneesh/cgi-bin/chat/chat.py?prune");
  };


  console.log("Create evtSource");

  let last_ts = "1970-01-01+00:00:00.00"
  let counter = 0;
  const listener = () => {
    const evtSource = new EventSource(`/~aneesh/cgi-bin/chat/chat.py?listen=${last_ts}`);
    evtSource.onopen = (e) => {
      console.log("Opening source");
    };
    evtSource.onmessage = (e) => {
      // TODO - have a max scrollback of `n` messages
      console.log("got message!");
      const newElement = document.createElement("div");
      const msg = JSON.parse(e.data);
      newElement.classList.add("msg");
      const message = atob(msg.message).trim().substr(4);
      newElement.innerHTML += `<div class='msgtimestamp'>${msg.timestamp}</div>`;
      if (message.startsWith("data:image")) {
        newElement.innerHTML += `<img class="msgimg" src="${message}"></img>`;
      } else {
        newElement.innerHTML += `<div class='msgcontent'>${message}</div>`;
      }
      newElement.innerHTML += `<br>`;
      chatroom.appendChild(newElement);

      setTimeout(() => { chatroom.scrollTop = chatroom.scrollHeight; }, 10);

      last_ts = msg.timestamp.replaceAll(' ', '+');
    };
    evtSource.onerror = (e) => {
      console.log("Closing source");
      evtSource.close();
      listener();
      counter += 1;
      if (counter % 4 == 0) {
        prune();
        counter = 0;
      }
    };
  };
  listener();
});
