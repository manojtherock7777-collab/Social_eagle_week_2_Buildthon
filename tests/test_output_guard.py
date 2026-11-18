
from backend.guardrails.output_guard import validate_output


def test_valid_output():

    answer = (
        "The Digital Crop Survey captures crop information "
        "using geotagged mobile applications."
    )

    documents = [
        {
            "source": "farmer_scheme.pdf",
            "page": "49",
            "content": "Digital Crop Survey information."
        }
    ]

    result = validate_output(answer, documents)

    print("\nValid output:")
    print(result)

    assert "Digital Crop Survey" in result
    assert "farmer_scheme.pdf" in result
    assert "Page 49" in result


def test_empty_output():

    result = validate_output("", [
        {
            "source": "farmer_scheme.pdf",
            "page": "49"
        }
    ])

    print("\nEmpty output:")
    print(result)

    assert "could not find sufficient information" in result


def test_no_retrieved_documents():

    result = validate_output(
        "Farmers can receive financial assistance.",
        []
    )

    print("\nNo retrieved documents:")
    print(result)

    assert "could not find sufficient information" in result


def test_duplicate_source_references():

    answer = "The document describes agricultural services."

    documents = [
        {
            "source": "farmer_scheme.pdf",
            "page": "49"
        },
        {
            "source": "farmer_scheme.pdf",
            "page": "49"
        },
        {
            "source": "farmer_scheme.pdf",
            "page": "38"
        }
    ]

    result = validate_output(answer, documents)

    print("\nDuplicate reference test:")
    print(result)

    assert result.count("Page 49") == 1
    assert result.count("Page 38") == 1


if __name__ == "__main__":

    test_valid_output()
    test_empty_output()
    test_no_retrieved_documents()
    test_duplicate_source_references()

    print("\nAll output guardrail tests passed!")
