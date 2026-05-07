// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);
const valL = document.getElementById('val-l');
const valR = document.getElementById('val-r');

// Initialize NippleJS Joystick
const manager = nipplejs.create({
    zone: document.getElementById('joystick-zone'),
    mode: 'static',
    position: { left: '50%', top: '50%' },
    color: '#008184',
    size: 180 // Slightly larger for better control
});

manager.on('move', (evt, data) => {
    if (!data.vector) return;

    const y = data.vector.y; 
    const x = data.vector.x; 
    
    // Reverse gear steering correction
    const steeringAdjust = (y < 0) ? -x : x;

    // Mixing Logic
    let left = 90 + (y * 90) + (steeringAdjust * 45);
    let right = 90 - (y * 90) + (steeringAdjust * 45);

    left = Math.max(0, Math.min(180, Math.round(left)));
    right = Math.max(0, Math.min(180, Math.round(right)));

    valL.textContent = left;
    valR.textContent = right;

    socket.emit('move_robot', { l: left, r: right });
});

manager.on('end', () => {
    socket.emit('move_robot', { l: 90, r: 90 });
    valL.textContent = 90;
    valR.textContent = 90;
});