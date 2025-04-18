const fs = require('fs');
const path = require('path');

// Function to walk through directories recursively
function walkSync(dir, filelist = []) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filepath = path.join(dir, file);
    const stat = fs.statSync(filepath);
    if (stat.isDirectory()) {
      filelist = walkSync(filepath, filelist);
    } else if (
      (filepath.endsWith('.js') || filepath.endsWith('.jsx')) && 
      !filepath.endsWith('.test.js') && 
      !file.startsWith('.') &&
      !filepath.includes('node_modules')
    ) {
      filelist.push(filepath);
    }
  });
  return filelist;
}

// Function to add React import to a file if it uses JSX but doesn't import React
function addReactImport(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // If file already has React import, skip it
    if (content.includes('import React')) {
      console.log(`✓ ${filePath} - Already has React import`);
      return;
    }
    
    // Check if file uses JSX (simplified check)
    if (content.includes('<') && content.includes('/>') || content.includes('</')) {
      // Find the first import statement
      const importIndex = content.indexOf('import ');
      
      if (importIndex !== -1) {
        // Add React import before first import
        const updatedContent = content.slice(0, importIndex) + 
          'import React from "react";\n' + 
          content.slice(importIndex);
        
        fs.writeFileSync(filePath, updatedContent);
        console.log(`✅ ${filePath} - Added React import`);
      } else {
        // Add React import at the beginning of the file
        const updatedContent = 'import React from "react";\n\n' + content;
        fs.writeFileSync(filePath, updatedContent);
        console.log(`✅ ${filePath} - Added React import at the beginning`);
      }
    } else {
      console.log(`⏭️ ${filePath} - No JSX found, skipping`);
    }
  } catch (error) {
    console.error(`❌ Error processing ${filePath}: ${error.message}`);
  }
}

// Start processing files in the src directory
const srcDir = path.join(__dirname, 'src');
console.log(`Scanning files in ${srcDir}...`);

const jsFiles = walkSync(srcDir);
console.log(`Found ${jsFiles.length} JavaScript files`);

// Process each file
jsFiles.forEach(file => {
  addReactImport(file);
});

console.log('Done!'); 