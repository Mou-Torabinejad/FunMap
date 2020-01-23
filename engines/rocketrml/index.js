const parser = require('rocketrml');
var fs = require('fs')

const doMapping = async () => {
  try{
    aux = fs.readFileSync('./data.csv', 'utf8')
    mapping = fs.readFileSync('mapping.rml.ttl', 'utf8')
  }catch(e){
     console.log('Error:', e.stack);
  }
  let inputFiles = {
      "data.csv": aux 
    };
  const options = {
    toRDF: true,
    verbose: true,
    xmlPerformanceMode: false,
    replace: false,
    functions: {
      'http://users.ugent.be/~bjdmeest/function/grel.ttl#toUpperCase': function (data) {
                let result=data[0].toUpperCase(); 
                return result;
         }
    }
  };
  const result = await parser.parseFileLive(mapping, inputFiles, options).catch((err) => { console.log(err); });
};

doMapping();
