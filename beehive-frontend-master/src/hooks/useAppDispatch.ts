import { useDispatch } from 'react-redux';

import type { AppDispatch } from '../store';

// replaces `useDispatch` so the correct type is available
const useAppDispatch = (): AppDispatch => useDispatch<AppDispatch>();

export default useAppDispatch;
