// Breaking News Feature Flag
const showBreakingNews = process.env.REACT_APP_BREAKING_NEWS === '1';

{showBreakingNews && (
  <MDAlert color="warning" sx={{ mb: 2 }}>
    Breaking News: Major economic event! (This is a feature-flagged component.)
  </MDAlert>
)} 