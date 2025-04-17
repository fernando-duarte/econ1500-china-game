import { useContext } from 'react';
import { BreakingNewsContext } from '../providers/BreakingNewsProvider';

/**
 * useBreakingNews hook to access breaking news context.
 */
export const useBreakingNews = () => useContext(BreakingNewsContext); 