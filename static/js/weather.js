(() => {
    'use strict';

    const card = document.querySelector('[data-weather-card]');
    if (!card) {
        return;
    }

    const statusEl = card.querySelector('[data-weather-status]');
    const currentTempEl = card.querySelector('[data-weather-current]');
    const currentDayEl = card.querySelector('[data-weather-day]');
    const forecastDayEls = Array.from(card.querySelectorAll('[data-weather-forecast-day]'));
    const forecastTempEls = Array.from(card.querySelectorAll('[data-weather-forecast-temp]'));

    const setStatus = (message, isError = false) => {
        if (!statusEl) {
            return;
        }
        statusEl.textContent = message;
        statusEl.classList.toggle('weather-card__status--error', isError);
        statusEl.classList.toggle('weather-card__status--hidden', !message);
    };

    const roundTemp = (value) => Math.round(value);

    const dayFormatter = new Intl.DateTimeFormat('en-US', {
        weekday: 'short',
        timeZone: 'America/Chicago'
    });

    const updateWeather = async () => {
        setStatus('Loading weather...');

        try {
            const endpoint = new URL('https://api.open-meteo.com/v1/forecast');
            endpoint.search = new URLSearchParams({
                latitude: '40.1106',
                longitude: '-88.2073',
                current: 'temperature_2m',
                daily: 'temperature_2m_max',
                temperature_unit: 'celsius',
                timezone: 'America/Chicago'
            }).toString();

            const response = await fetch(endpoint.toString(), { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`Weather request failed: ${response.status}`);
            }

            const data = await response.json();
            const currentTemp = data?.current?.temperature_2m;
            const dailyTemps = data?.daily?.temperature_2m_max;
            const dailyDates = data?.daily?.time;

            if (typeof currentTemp !== 'number' || !Array.isArray(dailyTemps) || !Array.isArray(dailyDates)) {
                throw new Error('Weather data missing');
            }

            if (currentTempEl) {
                currentTempEl.textContent = `${roundTemp(currentTemp)}°C`;
            }

            if (currentDayEl) {
                currentDayEl.textContent = dayFormatter.format(new Date());
            }

            const forecastStartIndex = 1;
            forecastDayEls.forEach((dayEl, index) => {
                const dataIndex = forecastStartIndex + index;
                const dateString = dailyDates[dataIndex];
                const tempValue = dailyTemps[dataIndex];

                if (!dateString || typeof tempValue !== 'number') {
                    return;
                }

                const dayLabel = dayFormatter.format(new Date(`${dateString}T00:00:00`));
                if (dayEl) {
                    dayEl.textContent = dayLabel;
                }

                const tempEl = forecastTempEls[index];
                if (tempEl) {
                    tempEl.textContent = `${roundTemp(tempValue)}°C`;
                }
            });

            setStatus('');
        } catch (error) {
            setStatus('Weather unavailable', true);
        }
    };

    updateWeather();
})();
