/**
 * Authentication and Authorization Middleware
 */

// Check if the user is authenticated
const isAuthenticated = (req, res, next) => {
  // In a real implementation, this would check for a valid JWT token
  // or session cookie
  
  // For now, we'll just check for the presence of a header
  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    return res.status(401).json({
      success: false,
      message: 'Authentication required'
    });
  }
  
  // In a real implementation, we would verify the token and set user info
  // req.user = { id: '123', role: 'admin', ... }
  
  // Mock user for development
  if (process.env.NODE_ENV !== 'production') {
    req.user = {
      id: 'dev-user-123',
      role: req.headers['x-user-role'] || 'user',
      name: 'Development User',
      email: 'dev@example.com'
    };
  }
  
  next();
};

// Check if the user is an admin
const isAdmin = (req, res, next) => {
  // First ensure user is authenticated
  if (!req.user) {
    return res.status(401).json({
      success: false,
      message: 'Authentication required'
    });
  }
  
  // Check if user has admin role
  if (req.user.role !== 'admin') {
    return res.status(403).json({
      success: false,
      message: 'Admin access required'
    });
  }
  
  next();
};

// Check if the user is a professor
const isProfessor = (req, res, next) => {
  // First ensure user is authenticated
  if (!req.user) {
    return res.status(401).json({
      success: false,
      message: 'Authentication required'
    });
  }
  
  // Check if user has professor role
  if (req.user.role !== 'professor' && req.user.role !== 'admin') {
    return res.status(403).json({
      success: false,
      message: 'Professor access required'
    });
  }
  
  next();
};

// Check if the user is a team member
const isTeamMember = (req, res, next) => {
  // First ensure user is authenticated
  if (!req.user) {
    return res.status(401).json({
      success: false,
      message: 'Authentication required'
    });
  }
  
  // Get team ID from request parameters
  const { teamId } = req.params;
  
  // In a real implementation, we would check if the user belongs to the team
  // For now, we'll just pretend all authenticated users can access all teams
  // if role is admin or professor, or if the team belongs to the user
  
  next();
};

// Check if the user is in the specified class
const isInClass = (req, res, next) => {
  // First ensure user is authenticated
  if (!req.user) {
    return res.status(401).json({
      success: false,
      message: 'Authentication required'
    });
  }
  
  // Get class ID from request parameters
  const { classId } = req.params;
  
  // In a real implementation, we would check if the user belongs to the class
  // For now, we'll just pretend all authenticated users can access all classes
  // if role is admin or professor, or if the class includes the user
  
  next();
};

module.exports = {
  isAuthenticated,
  isAdmin,
  isProfessor,
  isTeamMember,
  isInClass
}; 