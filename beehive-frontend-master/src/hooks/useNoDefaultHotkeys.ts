import { HotkeysEvent, KeyHandler } from 'hotkeys-js';
import React from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

const useNoDefaultHotkeys = (keys: string, callback: KeyHandler): React.MutableRefObject<Element | null> => {
    return useHotkeys(
        keys,
        (keyboardEvent: KeyboardEvent, hotkeysEvent: HotkeysEvent) => {
            // always prevent default action (otherwise for example for ctrl+s save window will pop up)
            keyboardEvent.preventDefault();

            // run callback only on keyup
            if (keyboardEvent.type === 'keyup') {
                return callback(keyboardEvent, hotkeysEvent);
            } else {
                return undefined;
            }
        },
        {
            keydown: true,
            keyup: true
        }
    );
};

export default useNoDefaultHotkeys;
