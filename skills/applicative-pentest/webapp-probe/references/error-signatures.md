# Error-page / stack-trace / debug-disclosure signatures (class 4)

Run over each captured response body **after** skipping JS bundles (body matches `sourceMappingURL|window\.addEventListener|window\.document|webpackJsonp|jQuery`). Any match is an "Improper Error Handling" finding: verbose errors leak stack frames, file paths, framework/DB versions, and gadget-chain internals. When loading into the `rules.txt` sweep, prefix each name with `ERR:` so the snippet skips them on JS bundles.

## Contents
- Database / SQL errors
- Language runtime exceptions
- Framework error pages
- Insecure-deserialization / gadget-chain traces
- Config / secret disclosure & debug mode
- CSRF / JWT / auth errors

## Database / SQL errors
| Name | Regex |
|---|---|
| Generic SQL error | `Database error: SQLSTATE` |
| Microsoft SQL Server error | `Microsoft OLE DB Provider for SQL Server` |
| MySQL syntax error | `You have an error in your SQL syntax` |
| SQL Injection Error | `SQL syntax error` |
| PostgreSQL error | `ERROR:  syntax error at or near` |
| Oracle SQL error | `ORA-\d+:` |
| DB2 SQL error | `DB2 SQL Error: SQLCODE=` |
| SQLite error | `SQLiteException` |
| MongoDB error | `E11000 duplicate key error collection` |
| Elasticsearch error | `type=\\\"mapper_parsing_exception\\\"` |

## Language runtime exceptions
| Name | Regex |
|---|---|
| Java exception | `java\.lang\.\w+Exception` |
| Java RuntimeException | `java\.lang\.RuntimeException` |
| NullPointerException | `java\.lang\.NullPointerException` |
| ArrayIndexOutOfBoundsException | `java\.lang\.ArrayIndexOutOfBoundsException` |
| ClassCastException | `java\.lang\.ClassCastException` |
| Java NumberFormatException | `java\.lang\.NumberFormatException` |
| Java StringIndexOutOfBoundsException | `java\.lang\.StringIndexOutOfBoundsException` |
| Java IllegalStateException | `java\.lang\.IllegalStateException` |
| Java ClassNotFoundException | `java\.lang\.ClassNotFoundException` |
| Java IOException | `java\.io\.IOException` |
| Java EOFException | `java\.io\.EOFException` |
| Java SQLException | `java\.sql\.SQLException` |
| PHP Parse error | `PHP Parse error` |
| PHP Warning | `PHP Warning` |
| PHP Notice | `PHP Notice` |
| Generic fatal error | `Fatal error` |
| Python Traceback error | `Traceback \(most recent call last\)` |
| Python ValueError | `ValueError:` |
| Python TypeError | `TypeError:` |
| Python ImportError | `ImportError:` |
| Python AttributeError | `AttributeError:` |
| Python KeyError | `KeyError:` |
| Python IndexError | `IndexError:` |
| Python MemoryError | `MemoryError` |
| Python RecursionError | `RecursionError` |
| Python ModuleNotFoundError | `ModuleNotFoundError` |
| Python OSError | `OSError` |
| Python OverflowError | `OverflowError` |
| Python ZeroDivisionError | `ZeroDivisionError` |
| Ruby error | `/[^\s]+.rb:\d+:` |
| Ruby ArgumentError | `ArgumentError` |
| Ruby LoadError | `cannot load such file --` |
| Ruby NameError | `: undefined local variable or method` |
| C++ std::exception | `std::exception` |
| C++ std::length_error | `std::length_error` |
| C++ std::bad_alloc | `std::bad_alloc` |
| .NET InvalidOperationException | `System\.InvalidOperationException` |
| NullReferenceException | `System\.NullReferenceException` |
| IndexOutOfRangeException | `System\.IndexOutOfRangeException` |

## Framework error pages
| Name | Regex |
|---|---|
| Ruby on Rails error | `ActionView::Template::Error` |
| Ruby on Rails Stack Trace | `^.+Error: .+\n(\s+at .+\:\d+(:\d+)?\n)+` |
| Ruby on Rails Database Error | `ActiveRecord::(.+?)Error` |
| Ruby on Rails Strong Parameters Error | `ActionController::ParameterMissing: param is missing or the value is empty` |
| Django ImportError | `ImportError: No module named` |
| Django OperationalError | `django.db.utils.OperationalError` |
| Django InterfaceError | `django.db.utils.InterfaceError` |
| Django FieldError | `django.core.exceptions.FieldError` |
| Django ValidationError | `value has an invalid format. It must be` |
| Django ObjectDoesNotExist | `django.core.exceptions.ObjectDoesNotExist` |
| Python Django Query Error | `FieldError: Cannot resolve keyword '.+' into field` |
| Python Django Technical Error | `Traceback \(most recent call last\):\n(\s+File \".+\", line \d+, in .+\n)+` |
| Flask KeyError | `KeyError: 'foo'` |
| Flask RuntimeError | `RuntimeError: Working outside of application context` |
| Flask Werkzeug Error | `werkzeug.exceptions.HTTPException` |
| Flask SQLAlchemy Error | `sqlalchemy.exc.InvalidRequestError` |
| Flask JWTExtendedException | `flask_jwt_extended.exceptions.JWTExtendedException` |
| Laravel ErrorException | `ErrorException in.*\.php` |
| Laravel QueryException | `Illuminate\\Database\\QueryException` |
| PHP Laravel Detailed Error | `#(\d+ )?\/path\/to\/file\.php\((\d+)\): .+\nStack trace:\n.+\n` |
| PHP Laravel Database Error | `PDOException: SQLSTATE\[\w+\]: .+` |
| Symfony FatalErrorException | `Symfony\\Component\\Debug\\Exception\\FatalErrorException` |
| Symfony NotFoundHttpException | `Symfony\\Component\\HttpKernel\\Exception\\NotFoundHttpException` |
| PHP Laravel Middleware Error | `Symfony\\Component\\HttpKernel\\Exception\\HttpException` |
| Spring NoSuchBeanDefinitionException | `org\.springframework\.beans\.factory\.NoSuchBeanDefinitionException` |
| Spring BeanCreationException | `org\.springframework\.beans\.factory\.BeanCreationException` |
| Spring DataIntegrityViolationException | `org.springframework.dao.DataIntegrityViolationException` |
| Spring HibernateJdbcException | `org.hibernate.exception.GenericJDBCException` |
| Java Spring Data Source Error | `org\.springframework\.jdbc\.CannotGetJdbcConnectionException` |
| Java Spring Data Access Error | `DataAccessException: .+` |
| Java Spring Bean Configuration | `Error creating bean with name '.+' defined in .+: .+` |
| Java Spring Boot Error | `org\.springframework\.boot\|Caused by:` |
| ASP.NET HttpException | `System.Web.HttpException` |
| ASP.NET HttpParseException | `System.Web.HttpParseException` |
| ASP.NET SqlException | `System.Data.SqlClient.SqlException` |
| ASP.NET FileNotFoundException | `System.IO.FileNotFoundException` |
| ASP.NET Detailed Error Page | `Server Error in '/.*' Application` |
| Express.js CastError | `CastError: Cast to ObjectId failed` |
| Express.js Detailed Error | `at .* \(.+:\d+:\d+\)` |
| Express.js Middleware Error | `Error: (Failed to find|Cannot find) module .+` |
| Express.js MongoError | `MongooseServerSelectionError` |
| Node.js MongoDB Error | `MongoError: .+` |
| Custom Class Method Invocation | `\w+\.\w+\.main.*.java\:` |

## Insecure-deserialization / gadget-chain traces
| Name | Regex |
|---|---|
| Go Deserialization Error (gob) | `gob: type not registered for interface` |
| Golang encoding/gob Decoding Error | `encoding/gob` |
| Java Hashtable.readObject Error | `java\.util\.Hashtable\.readObject` |
| Java Hashtable.reconstitutionPut Error | `java\.util\.Hashtable\.reconstitutionPut` |
| Apache Commons AbstractMapDecorator.equals Error | `org\.apache\.commons\.collections\.map\.AbstractMapDecorator\.equals` |
| Java AbstractMap.equals Error | `java\.util\.AbstractMap\.equals` |
| Apache Commons LazyMap.get Error | `org\.apache\.commons\.collections\.map\.LazyMap\.get` |
| Apache Commons ChainedTransformer.transform Error | `org\.apache\.commons\.collections\.functors\.ChainedTransformer\.transform` |
| Apache Commons InvokerTransformer.transform Error | `org\.apache\.commons\.collections\.functors\.InvokerTransformer\.transform` |
| Java Reflection Method.invoke Error | `java\.lang\.reflect\.Method\.invoke` |
| Java DelegatingMethodAccessorImpl.invoke Error (sun) | `sun\.reflect\.DelegatingMethodAccessorImpl\.invoke` |
| Java NativeMethodAccessorImpl.invoke Error (sun) | `sun\.reflect\.NativeMethodAccessorImpl\.invoke` |
| Java NativeMethodAccessorImpl.invoke0 Error (sun) | `sun\.reflect\.NativeMethodAccessorImpl\.invoke0` |
| Java NativeMethodAccessorImpl.invoke Error (jdk) | `jdk\.internal\.reflect\.NativeMethodAccessorImpl\.invoke` |
| Java DelegatingMethodAccessorImpl.invoke Error (jdk) | `jdk\.internal\.reflect\.DelegatingMethodAccessorImpl\.invoke` |
| Java Runtime.exec Error | `java\.lang\.Runtime\.exec` |
| Java WriteAbortedException Error | `java\.io\.WriteAbortedException: writing aborted; java\.io\.NotSerializableException` |
| Java NotSerializableException Error | `java\.io\.NotSerializableException: \w+\.\w+` |
| Java ObjectOutputStream.writeObject0 Error | `java\.io\.ObjectOutputStream\.writeObject0` |
| Java ObjectInputStream.readObject Error | `java\.io\.ObjectInputStream\.readObject` |
| Java ArrayList.writeObject Error | `java\.util\.ArrayList\.writeObject` |
| Java ArrayList.readObject Error | `java\.util\.ArrayList\.readObject` |
| Java ObjectStreamClass.invokeReadObject Error | `java\.io\.ObjectStreamClass\.invokeReadObject` |
| Java ObjectOutputStream.writeSerialData Error | `java\.io\.ObjectOutputStream\.writeSerialData` |
| Java ObjectInputStream.readOrdinaryObject Error | `java\.io\.ObjectInputStream\.readOrdinaryObject` |
| Java ObjectOutputStream.writeObject Error | `java\.io\.ObjectOutputStream\.writeObject` |
| Java ObjectStreamClass.invokeWriteObject Error | `java\.io\.ObjectStreamClass\.invokeWriteObject` |
| Java ObjectOutputStream.writeOrdinaryObject Error | `java\.io\.ObjectOutputStream\.writeOrdinaryObject` |
| Java Serialization Error | `java\.io\.Object(I\|O)Stream` |
| Python pickle Unpickling Error | `pickle\.UnpicklingError` |
| Python PyYAML Deserialization Error | `yaml\.load\(` |
| PHP unserialize Error | `unserialize\(` |
| Ruby YAML.load Error | `YAML\.load\(` |
| Ruby on Rails Marshal.load Error | `Marshal\.load` |
| C# BinaryFormatter Deserialization Error | `System\.Runtime\.Serialization\.Formatters\.Binary\.BinaryFormatter` |
| Perl Storable Error | `Storable::thaw` |
| Django PickleField Unpickling Error | `django\.db\.models\.fields\.PickleField` |
| Flask-Session Pickle Deserialization Error | `flask_session\.sessions\.TaggedJSONSerializer` |
| Spring Framework Java Deserialization Error | `org\.springframework\.core\.deserialize\.` |
| Node.js unserialize-javascript Error | `unserialize-javascript` |
| Java Jackson JSON Deserialization Error | `com\.fasterxml\.jackson\.databind` |
| Command Injection Error | `Command execution error` |

## Config / secret disclosure & debug mode
| Name | Regex |
|---|---|
| ASP.NET Web.config Error (debug) | `<compilation debug=\"true\"` |
| ASP.NET Web Config comment | `<!--\s*Web\.Config Configuration File\s*-->` |
| Django Debug = True enabled | `your Django settings file. Change that to` |
| Python Django Database Configuration | `DATABASES = \{.+}` |
| Ruby on Rails Secret Key Base | `config\.secrets\.secret_key_base` |
| Node.js Configuration Disclosure | `ConfigurationError: \|Failed to read config file: .+\.json` |
| Node.js Invalid Configuration | `Error: Invalid configuration: .+` |
| Java Spring Security Misconfiguration | `org\.springframework\.security` |

## CSRF / JWT / auth errors
| Name | Regex |
|---|---|
| Express.js CSRF Token Error | `TokenMismatchException: CSRF token mismatch` |
| Ruby on Rails CSRF Error | `ActionController::InvalidAuthenticityToken` |
| Python Django CSRF Error | `CSRF verification failed` |
| PHP Laravel CSRF Token Error | `TokenMismatchException in VerifyCsrfToken.php` |
| Java Spring Security CSRF Error | `Invalid CSRF Token 'null' was found on the request parameter '_csrf' or header 'X-CSRF-TOKEN'` |
| Node.js JWT Error | `JsonWebTokenError: .+` |
| Express.js JWT Error | `UnauthorizedError: .+` |

Note: the source list contained several exact duplicates (e.g. `java.io.IOException`, `Illuminate\\Database\\QueryException`, `ObjectOutputStream.writeOrdinaryObject`, `NativeMethodAccessorImpl.invoke` in both `sun.reflect` and `jdk.internal.reflect`) - collapsed to one row each here without losing any distinct pattern.
