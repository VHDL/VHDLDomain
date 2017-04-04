# sphinxcontrib-vhdldomain

This sphinx extension adds a new language domain to Sphinx. It allows the documentation of VHDL source files.




**License: Apache 2.0**


# VHDL Domain

## Directives

#### Library

```rst
.. vhdl:library:: myLibrary

   Description text
```

### Design Unit Directives


#### Context

```rst
.. vhdl:context:: myContext

   Description text
```

#### Entity

```rst
.. vhdl:entity:: myEntity

   Description text
```


#### Architecture

```rst
.. vhdl:architecture:: rtl
   :entity: myEntity

   Description text
```


#### Package

```rst
.. vhdl:package:: myPackage

   Description text
```


#### Package Body

```rst
.. vhdl:packagebody:: myPackage

   Description text
```


#### Configuration

```rst
.. vhdl:package:: myConfiguration

   Description text
```


### Nested Directives

#### UseClause

```rst
.. vhdl:use:: IEEE.std_logic_1164.all

   Description text
```


#### ContextClause

```rst
.. vhdl:ctx:: work.myContext

   Description text
```


#### EnumerationType

```rst
.. vhdl:enum:: myState
   :literals: IDLE, WORKING, ERROR

   Description text
```


#### IntegerType

```rst
.. vhdl:integer:: myInteger
   :range: 0 to 255

   Description text
```


#### PhysicalType

```rst
.. vhdl:physical:: myFrequency
   :primary: Hz
   :secondary: kHz=1000 Hz, MHz=1000kHz, GHz=1000MHz

   Description text
```


#### FloatingType

```rst
.. vhdl:float:: myReal
   :range: 0.0 to 1.0

   Description text
```


#### ArrayType

```rst
.. vhdl:array:: myArray
   :elementType: bit
   :indexTypes: natural range <>, natural range <>

   Description text
```

#### RecordType

```rst
.. vhdl:record:: myRecord
   :elements: element1:string, element2:integer

   Description text
```

#### Access Type


#### File Type


#### Protected Type

```rst
.. vhdl:protected:: myProtected

   Description text
```

#### SubType


#### Alias


#### Constant

```rst
.. vhdl:constant:: myConstant
   :type:
   :init:

   Description text
```

#### Signal

```rst
.. vhdl:signal:: mySignal
   :type:
   :init:

   Description text
```

#### SharedVariable

```rst
.. vhdl:sharedvar:: mySharedVariable
   :type:

   Description text
```

#### Function

```rst
.. vhdl:function:: function myfunction(a : integer) return string;
   :method:
   :pure:
   :impure:

   Description text
```

#### Procedure

```rst
.. vhdl:procedure:: myprocedure(a : integer)
   :method:

   Description text
```

#### Parameter

```rst
.. vhdl:parameter:: a : integer

   Description text
```

#### Return Type

```rst
.. vhdl:returntype:: string

   Description text
```

## Roles

### Design Unit Roles

#### Context

#### Entity

#### Architecture

#### Package

#### Configuration

### Other Roles

#### Type

#### Function

#### Procedure

#### Subprogram

## Indices

#### EntityIndex

#### PackageIndex

#### TypeIndex
