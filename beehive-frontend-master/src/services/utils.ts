/** Converts duration (in seconds) to a string */
export function durationSecondsAsString(secs: number): string {
    const wholeSecs = Math.floor(secs);
    const hours = Math.floor(wholeSecs / 3600);
    const minutes = Math.floor((wholeSecs / 60) % 60);

    return (String(hours).padStart(2, '0') + ':' + String(minutes).padStart(2, '0'));
}

export function testUrl(url: string): Promise<void> {
    // make a normal GET fetch. if it fails return rejected promise, otherwise return resolved
    return fetch(url)
        .catch(() => Promise.reject())
        .then(() => Promise.resolve());
}

export function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export function humanize(str: string): string {
    return str
        .replace(/^[\s_]+|[\s_]+$/g, '')
        .replace(/[_\s]+/g, ' ')
        .replace(/(\b[a-z](?!\s))/g, function (m) { 
            return m.toUpperCase(); 
        });
}
