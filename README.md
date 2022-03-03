# SoapTools
Tools package to help in work with SOAP, XSD thingies.
Currently client is somewhat wrapper of Zeep client. I hope to remove this dependency soon. 

For documentation look [here](docs/main.md)

## Requirements:
- Python 3.9
- lxml (installation can cause problems sometimes)

## Features
- generate fully typed SOAP service client
- generate xs python bindings from wsdl file or .xsd in human readable shape

## versioning
https://semver.org/lang/pl/

## Planned features
- parsing <wsdl: policy>
- check how java server does its magin

## Usage
###1. Get help info 
`python -msoaptools --help` or `python -msoaptools <command> --help` 

###2. Generate soap service client class [look [here](docs/generate-client.md)] 
```bash
  python -msoaptools generate-client <wsdl_url> <output_foler_name>
```

###3. Generate python bindings [look [here](docs/generate-bindings.md)] 

#### 3.1 from wsdl
```bash
  python -msoaptools generate-bindings --from-wsdl <URL or filesystem path> --output-filepath somefile.py
```

#### 3.2 from xsd
```bash
  python -msoaptools generate-bindings --from-xsd <URL or filesystem path> --output-filepath somefile.py
```

## TODO:
![MOAR UNIT TESTS](https://memegenerator.net/img/instances/69608142/unit-tests.jpg)
- generating valid XMLs from XSD
- support MOAR `<xs:restriction>` children
- support Policy parsing
- MOAR everything


###Used packages:
- zeep - https://github.com/mvantellingen/python-zeep
- lxml - https://github.com/lxml/lxml
- requests - https://github.com/psf/requests
- black - https://github.com/psf/black