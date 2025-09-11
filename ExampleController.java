@RestController
public class ExampleController {

    private final ExampleUseCase exampleUseCase;

    public ExampleController(ExampleUseCase exampleUseCase) {
        this.exampleUseCase = exampleUseCase;
    }

    @PostMapping("api/v1/example")
    public V1OutDto v1(@RequestBody V1InDto v1InDto) {

        // 関連チェック
        v1InDto.combineCheck();

        // ユースケース実行
        final var usecaseResult = exampleUseCase.exec(v1InDto.minMaxValue);

        // 後で消す
        usecaseResult.applicationClassificationList().forEach(it -> {
            it.applicationClassificationId();
            it.applicationTypeDiv();
            it.applicationClassificationName();
            it.applicationClassificationDescription();
            it.sortControl();
            it.lastUpdateTimestamp();
        });

        final var result = new V1OutDto(
            v1InDto.name,
            v1InDto.nullableValue,
            v1InDto.minmax.toString(),
            new V1OutDtoInnerObject(
                v1InDto.inDtoInnerObject.innerName,
                v1InDto.inDtoInnerObject.innerLong.toString()
            ),
            v1InDto.inDtoArrayObjectList.stream().map(it -> new V1OutDtoArrayObject(
                it.arrayName
            )).toList(),
            v1InDto.instantValue,
            v1InDto.exampleEnum.getCode()
        );

        result.check();
        return result;
    }


    // 入力用DTO
    public record V1InDto(
        @UnitCheckString(
            pattern = UnitCheckString.Type.jisX0213withAlphaNumericSymbol
        )
        String name,

        @UnitCheckString(
            isRequired = false,
            pattern = UnitCheckString.Type.all
        )
        String nullableValue,

        @UnitCheckString(
            isRequired = false,
            pattern = UnitCheckString.Type.all
        )
        String notEmpty,

        @UnitCheckString(
            maxLength = 20,
            pattern = UnitCheckString.Type.all
        )
        String maxLengthValue,

        @UnitCheckString(
            pattern = UnitCheckString.Type.alphanumericPattern
        )
        String alphanumericValue,

        @UnitCheckNumber(
            minLength = 5,
            maxLength = 10
        )
        Long minMaxValue,

        @UnitCheckObject
        V1InDtoInnerObject inDtoInnerObject,

        @UnitCheckArray(
            minLength = 2,
            maxLength = 10
        )
        List<V1InDtoArrayObject> inDtoArrayObjectList,

        @UnitCheckInstant
        Instant instantValue,

        @UnitCheckEnum
        ExampleEnum exampleEnum
    ) {

        public void combineCheck() {
            // TODO: 開発者が実装する
        }
    }

    public record V1InDtoInnerObject(
        @UnitCheckString(
            pattern = UnitCheckString.Type.all
        )
        String innerName,
        @UnitCheckNumber
        Long innerLong
    ) {
    }

    public record V1InDtoArrayObject(
        @UnitCheckString(
            pattern = UnitCheckString.Type.all
        )
        String arrayName
    ) {
    }

    // 出力用DTO
    public record V1OutDto(
        String name,
        String nullableValue,
        String notEmpty,
        String maxLengthValue,
        String alphanumericValue,
        String minMaxValue,
        V1OutDtoInnerObject inDtoInnerObject,
    ) {
        public void check() {
            // TODO: 開発者が実装する
        }
    }

    public record V1OutDtoInnerObject(
        String innerName,
        String innerLong
    ) {
        public void check() {
            // TODO: 開発者が実装する
        }
    }

    public record V1OutDtoArrayObject(
        String arrayName
    ) {
        public void check() {
            // TODO: 開発者が実装する
        }
    }
}