/**
 * Script to fix import paths in the theme-dark and theme directories
 */
const fs = require('fs');
const path = require('path');

// Root directories
const themeDarkDir = path.join(__dirname, 'src/assets/theme-dark');
const themeDir = path.join(__dirname, 'src/assets/theme');

// Process files in a directory recursively
function processDirectory(dir) {
  const files = fs.readdirSync(dir, { withFileTypes: true });
  
  files.forEach(file => {
    const filePath = path.join(dir, file.name);
    
    if (file.isDirectory()) {
      processDirectory(filePath);
    } else if (file.name.endsWith('.js')) {
      fixImports(filePath);
    }
  });
}

// Fix imports in a file
function fixImports(filePath) {
  try {
    // Read the file content
    let content = fs.readFileSync(filePath, 'utf8');
    const isThemeDark = filePath.includes('theme-dark');
    const baseDir = isThemeDark ? 'assets/theme-dark' : 'assets/theme';
    
    // Calculate the relative depth
    const relativePath = path.relative(isThemeDark ? themeDarkDir : themeDir, path.dirname(filePath));
    const depth = relativePath.split(path.sep).length;
    
    // Fix imports patterns
    if (depth === 0) {
      // Root level of theme or theme-dark
      content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/base/`, 'g'), 'import $1 from "./base/');
      content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/functions/`, 'g'), 'import $1 from "./functions/');
      content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/components/`, 'g'), 'import $1 from "./components/');
    } else if (depth === 1) {
      // First level down (base, functions, or components)
      if (relativePath === 'base') {
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/base/`, 'g'), 'import $1 from "./');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/functions/`, 'g'), 'import $1 from "../functions/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/components/`, 'g'), 'import $1 from "../components/');
      } else if (relativePath === 'functions') {
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/base/`, 'g'), 'import $1 from "../base/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/functions/`, 'g'), 'import $1 from "./');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/components/`, 'g'), 'import $1 from "../components/');
      } else if (relativePath === 'components') {
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/base/`, 'g'), 'import $1 from "../base/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/functions/`, 'g'), 'import $1 from "../functions/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/components/`, 'g'), 'import $1 from "./');
      }
    } else if (depth === 2) {
      // Components subdirectories
      if (relativePath.startsWith('components/')) {
        const componentDir = relativePath.split('/')[1];
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/base/`, 'g'), 'import $1 from "../../base/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/functions/`, 'g'), 'import $1 from "../../functions/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/components/${componentDir}/`, 'g'), 'import $1 from "./');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/components/`, 'g'), 'import $1 from "../../components/');
      }
    } else if (depth === 3) {
      // Deeper level subdirectories
      if (relativePath.startsWith('components/')) {
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/base/`, 'g'), 'import $1 from "../../../base/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/functions/`, 'g'), 'import $1 from "../../../functions/');
        content = content.replace(new RegExp(`import (.*?) from ["']${baseDir}/components/`, 'g'), 'import $1 from "../../../components/');
      }
    }
    
    // Write back the content
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Fixed imports in ${filePath}`);
  } catch (error) {
    console.error(`Error processing file ${filePath}:`, error);
  }
}

// Start processing
console.log("Processing theme-dark directory...");
processDirectory(themeDarkDir);
console.log("Processing theme directory...");
processDirectory(themeDir);
console.log("Done!"); 