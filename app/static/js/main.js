let aliveSecond = 0;
let heartBeatRate = 5000;
let pubnub;
let appChannel = "face_recognition";
let stateChannel = "face_recognition_state";
let ttl = 60;


function setupPubNub() {
    pubnub = new PubNub({
        publishKey: 'pub-c-09ac2b2d-7d42-488c-b044-7c0cd64110b4',
        subscribeKey: 'sub-c-d26f2c06-f451-49de-8639-4b3b4c9f6928',
        secretKey: 'sec-c-YjM1NmFjYWYtZWRiYi00Y2UzLWIzNjctNjVmOWI5N2ZiMzk2',
        //cryptoModule: PubNub.CryptoModule.aesCbcCryptoModule({cipherKey: 'sd3b_secret'}),
        uuid: "2"
    });
    //create a channel
    const channel = pubnub.channel(appChannel);
    //create a subscription
    const subscription = channel.subscription();
    console.log('subscription', subscription);

    pubnub.addListener({
        message: (messageEvent) => {
            handleMessage(messageEvent.message);
        },
        status: (statusEvent) => {
            console.log('Status:', statusEvent.category);
        }
    });

    subscription.onMessage = (messageEvent) => {
        handleMessage(messageEvent.message);
    };

    subscription.subscribe();
};

function handleMessage(message) {
    console.log(message)
    if ("message" in message) {
        message = message["message"]
    }
    if (message.camera_status) {
        const el = document.getElementById("camera_status");
        if (message.camera_status == '1') {
            if (el) {
                el.innerHTML = "Camera Status: On";
            }
        } else {
            el.innerHTML = "Camera Status: Off";
        }
    }

    if (message.employee_identified && message.employee_identified == 1) {
        handleArrival(message.employee_id);

        const identification_status = document.getElementById("identification_status");
        if (identification_status) { identification_status.innerHTML = "Employee Successfully Identified"; }
    } else {
        const identification_status = document.getElementById("identification_status");
        if (identification_status) { identification_status.innerHTML = ""; }
    }

    if (message.confidence) {
        const confidence = document.getElementById("confidence");
        if (confidence) { confidence.innerHTML = `Confidence: ${message.confidence}`; }
    } else {
        const confidence = document.getElementById("confidence");
        if (confidence) { confidence.innerHTML = ""; }
    }

    if (message.photo_taken && message.photo_taken == 1) {
        const status = document.getElementById("photo_status");
        if (status) { status.innerHTML = "Photo taken successfully"; }
    }
}

const publishMessage = async(message) => {
    const publishPayload = {
        channel: appChannel,
        message: {
            message:message
        },
    };
    await pubnub.publish(publishPayload);
}

function subscribe()
{
    // console.log("Trying to subscribe with token");
	pubnub.subscribe({channels:[appChannel]});
    // const channel = pubnub.channel(appChannel);
    //create a subscription
    // const subscription = channel.subscription();
    // subscription.subscribe();
}



function handleArrival(employee_id) {
    const currentDateTime = new Date();

    const timeOfArrival = currentDateTime.toTimeString().split(' ')[0];
    const timeOfDepartureDate = new Date(currentDateTime.getTime() + 8 * 60 * 60 * 1000);

    fetch(`/create/attendance/${employee_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(
            {
                "date": currentDateTime.toISOString().split('T')[0],
                "time_of_arrival": timeOfArrival
            }
        )
    })
    .then(response => response.json())
    .then(data => {
        console.log("Attendance recorded successfully:", data);
    })
    .catch(error => {
        console.error("Error sending attendance data:", error);
    });

    // window.location.href = `/index`;
};

function handleDeparture(employee_id) {
    const currentDateTime = new Date();
    
    const timeOfDepartureDate = new Date(currentDateTime.getTime() + 8 * 60 * 60 * 1000);
    const timeOfDeparture = timeOfDepartureDate.toTimeString().split(' ')[0];
    
    fetch(`/update/attendance/${employee_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(
            {
                "time_of_departure": timeOfDeparture
            }
        )
    })
    .then(response => response.json())
    .then(data => {
        console.log("Attendance updated successfully:", data);
    })
    .catch(error => {
        console.error("Error sending attendance data:", error);
    });

    // window.location.href = `/index`;
};

function handleAttendanceRedirect(id) {
    window.location.href = `/attendance/${id}`;
    console.log(id);
}

function handleTakePhoto(employee_id) {
    console.log({
        "camera_status": 0,
        "employee_identified": 0,
        "take_photo": 1,
        "photo_taken": 0,
        "employee_id": employee_id
    })

    publishMessage(
        {
            "camera_status": 0,
            "employee_identified": 0,
            "take_photo": 1,
            "photo_taken": 0,
            "employee_id": employee_id
        }
    )
}

