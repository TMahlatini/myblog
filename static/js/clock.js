(() => {
    'use strict';

    const clockDisplay = document.querySelector('[data-clock="urbana"]');
    if (!clockDisplay) {
        return;
    }

    const formatter = new Intl.DateTimeFormat('en-GB', {
        timeZone: 'America/Chicago',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });

    let lastValue = '';

    const updateClock = () => {
        const now = new Date();
        const currentValue = formatter.format(now);

        if (currentValue !== lastValue) {
            clockDisplay.textContent = currentValue;
            lastValue = currentValue;
        }

        window.requestAnimationFrame(updateClock);
    };

    updateClock();
})();
