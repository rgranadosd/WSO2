module.exports = {
  presets: [
    ['@babel/preset-env', { targets: "defaults" }],
    ['@babel/preset-typescript', { 
      allExtensions: true, 
      isTSX: true 
    }]
  ]
};
