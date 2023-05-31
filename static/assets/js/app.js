$(document).ready(function () {
  const ctx = document.getElementById("myChart").getContext("2d");
  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{ label: "Humidity",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(39, 245, 213, 0.8)',],
    },
  });
  const ctx2 = document.getElementById("myChart2").getContext("2d");
  const myChart2 = new Chart(ctx2, {
    type: "line",
    data: {
      datasets: [{ label: "Temperature",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(131, 245, 39, 0.8)',],
    },
  });
  const ctx3 = document.getElementById("myChart3").getContext("2d");
  const myChart3 = new Chart(ctx3, {
    type: "line",
    data: {
      datasets: [{ label: "CO2",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(114, 39, 245, 0.8)',],
    },
  });
  const ctx4 = document.getElementById("myChart4").getContext("2d");
  const myChart4 = new Chart(ctx4, {
    type: "line",
    data: {
      datasets: [{ label: "UV",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(226, 245, 39, 0.8)',],
    },
  });
  function addData(label, data) {
    myChart.data.labels.push(label);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart.update();
  }
  function removeFirstData() {
    myChart.data.labels.splice(0, 1);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }
  function addData2(label, data) {
    myChart2.data.labels.push(label);
    myChart2.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart2.update();
  }
  function removeFirstData2() {
    myChart2.data.labels.splice(0, 1);
    myChart2.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }
  function removeFirstData3() {
    myChart3.data.labels.splice(0, 1);
    myChart3.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }
  function addData3(label, data) {
    myChart3.data.labels.push(label);
    myChart3.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart3.update();
  }

  function removeFirstData4() {
    myChart4.data.labels.splice(0, 1);
    myChart4.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }
  function addData4(label, data) {
    myChart4.data.labels.push(label);
    myChart4.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart4.update();
  }
  const MAX_DATA_COUNT = 20;
  //connect to the socket server.
  //   var socket = io.connect("http://" + document.domain + ":" + location.port);
  var socket = io.connect();
  //receive details from server
  socket.on("updateSensorState", function (msg) {
    console.log("Received sensorState :: " + msg.date + " :: " + msg.value);
    var elemento=document.getElementById("nodeState1");
    elemento.innerHTML=`${msg.value}`;
  });
  socket.on("updateSensorState2", function (msg) {
    console.log("Received sensorState :: " + msg.date + " :: " + msg.value);
    var elemento=document.getElementById("nodeState2");
    elemento.innerHTML=`${msg.value}`;
  });
  socket.on("updateSensorState3", function (msg) {
    console.log("Received sensorState :: " + msg.date + " :: " + msg.value);
    var elemento=document.getElementById("nodeState3");
    elemento.innerHTML=`${msg.value}`;
  });
  socket.on("updateSensorState4", function (msg) {
    console.log("Received sensorState :: " + msg.date + " :: " + msg.value);
    var elemento=document.getElementById("nodeState4");
    elemento.innerHTML=`${msg.value}`;
  });
  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);
    // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData();
    }
    var elemento=document.getElementById("humidity");
    elemento.innerHTML=`${msg.value}`;
    addData(msg.date, msg.value);
  });
  socket.on("updateSensorData2", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);
    // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData2();
    }
    var elemento=document.getElementById("temperature");
    elemento.innerHTML=`${msg.value}°C`;
    addData2(msg.date, msg.value);
  });
  socket.on("updateSensorData3", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);
    // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData3();
    }
    var elemento=document.getElementById("co2");
    elemento.innerHTML=`${msg.value}ppm`;
    addData3(msg.date, msg.value);
  });
  socket.on("updateSensorData4", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);
    // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData4();
    }
    var elemento=document.getElementById("uv");
    elemento.innerHTML=msg.value;
    addData4(msg.date, msg.value);
  });
});
