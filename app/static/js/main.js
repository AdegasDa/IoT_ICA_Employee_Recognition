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
    if (message.take_photo) {
        const takePhotoStatus = document.getElementById("photo_status");
        if (takePhotoStatus) { takePhotoStatus.innerHTML = "The photo is being taken"; }
    }

    if (message.employee_identified) {
        handleArrival(message.user_id);

        const identification_status = document.getElementById("identification_status");
        if (identification_status) { identification_status.innerHTML = "Employee Successfully Identified"; }
    }

    if (message.photo_taken == 1) {
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



function handleArrival(user_id) {
    const currentDateTime = new Date();

    const timeOfArrival = currentDateTime.toTimeString().split(' ')[0];
    const timeOfDepartureDate = new Date(currentDateTime.getTime() + 8 * 60 * 60 * 1000);

    fetch(`/create/attendance/${user_id}`, {
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
};

function handleDeparture(user_id) {
    const currentDateTime = new Date();

    const timeOfDepartureDate = new Date(currentDateTime.getTime() + 8 * 60 * 60 * 1000);
    const timeOfDeparture = timeOfDepartureDate.toTimeString().split(' ')[0];

    fetch(`/update/attendance/${user_id}`, {
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
};

function handleAttendanceRedirect(id) {
    window.location.href = `/attendance/${id}`;
    console.log(id);
}

function handleTakePhoto(employee_id) {
    publishMessage(
        {
            "employee_id": employee_id,
            "take_photo": 1,
            "employee_identified": 0,
            "photo_taken": 0
        }
    )
}

