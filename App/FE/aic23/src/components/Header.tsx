import {
  Input,
  Button,
  Drawer,
  Empty,
  Select,
  Dropdown,
  MenuProps,
  SelectProps,
  InputNumber,
} from "antd";
import { useState, FC } from "react";
import { ImageType } from "../types";
import { useSubmission } from "../context";
// import { wait } from "../utils";
import axiosClient from "../utils/axios";
import { getFolder } from "../utils";
import labelObjs from './objLabels.json';


type HeaderProps = {
  setImages: React.Dispatch<React.SetStateAction<ImageType[]>>;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  images: ImageType[];
};

const items = [
  {
    label: "clipmodel",
    value: "/clipmodel",
  },
  {
    label: "filename",
    value: "/filename",
  },
  {
    label: "kosmosmodel",
    value: "/kosmosmodel",
  },
];

type Color = { id: number; color: string[] };

type Filter =
  | {
      id: number;
      type: "obj";
      label: string;
      color: Color[];
      qty: number | null;
    }
  | {
      id: number;
      type: "ocr";
      label: "";
    };

const Header: FC<HeaderProps> = ({ setImages, loading, setLoading }) => {
  const [openCSV, setOpenCSV] = useState(false);
  const [select, setSelect] = useState("/clipmodel");
  const { submissions, removeSubmission, clearSubmission, downloadSubmission } =
    useSubmission();
  const [filters, setFilters] = useState<Filter[]>([]);

  console.log(filters);

  const labels: SelectProps["options"] = labelObjs;
  //  [
  //   {
  //     label: "a",
  //     value: "a",
  //   },
  //   {
  //     label: "Person",
  //     value: "Person",
  //   },
  //   {
  //     label: "b",
  //     value: "b",
  //   },
  // ];

  const dropdown: MenuProps["items"] = [
    {
      label: "Object",
      key: "object",
      disabled:
        filters.filter((filter) => filter.type === "obj").length >=
        labels.length,
      onClick: () => addFilter("obj"),
    },
    {
      label: "OCR",
      key: "ocr",
      disabled: filters.some((value) => value.type === "ocr"),
      onClick: () => addFilter("ocr"),
    },
  ];

  const colors = [
    {
      label: "a",
      value: "a",
    },
    {
      label: "b",
      value: "b",
    },
  ];

  const addFilter = (type: "ocr" | "obj") => {
    if (type === "ocr" && filters.some((value) => value.type === "ocr")) return;
    if (
      type === "obj" &&
      filters.filter((filter) => filter.type === "obj").length >= labels.length
    )
      return;
    if (type === "ocr") {
      setFilters((prev) => [
        ...prev,
        {
          id: Date.now(),
          label: "",
          type: "ocr",
        },
      ]);
      return;
    }
    setFilters((prev) => [
      ...prev,
      {
        id: Date.now(),
        label: "",
        type: "obj",
        qty: null,
        color: [
          {
            id: Date.now() + 1,
            color: [],
          },
        ],
      },
    ]);
  };

  const onSearch = async (value: string) => {
    if (!value) return;
    try {
      setLoading(true);
      const { data } = await axiosClient.post<ImageType[]>(select, {
        query: value,
      });
      setImages(data);
      console.log(data);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  const onApply = async () => {
    const labels = [] as string[];
    const qtys = [] as number[];
    const colors = [] as string[][][];
    const ocr = filters.find((filter) => filter.type === "ocr")?.label || "";

    for (const filter of filters) {
      if (filter.type === "ocr") continue;
      const { color, label, qty } = filter;
      labels.push(label);
      if (qty === null) {
        qtys.push(color.length);
        colors.push([...new Set(color.map((c) => c.color)).values()]);
        continue;
      }
      qtys.push(qty);
      colors.push([...Array(qty)].map(() => color[0].color));
    }

    try {
      setLoading(true);
      const { data } = await axiosClient.post<ImageType[]>("/filter", {
        labels,
        qtys,
        colors,
        ocr,
      });
      setImages(data);
      console.log(data);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  const onRemove = (id: number) => {
    setFilters((prev) => prev.filter((filter) => filter.id !== id));
  };

  return (
    <>
      <div className="z-10 bg-white p-4 flex flex-col gap-4 sticky top-0 shadow h-screen min-w-[20vw] overflow-auto">
        <div className="flex gap-4 items-center">
          <Button type="primary" onClick={() => setOpenCSV((prev) => !prev)}>
            CSV
          </Button>
          <Select
            showSearch
            className="w-full"
            options={items}
            value={select}
            onChange={setSelect}
          />
        </div>
        <Input.Search
          enterButton
          allowClear
          onSearch={onSearch}
          disabled={loading}
        />
        <div className="flex items-center ">
          <span>Filter</span>
          <Button
            type="primary"
            className="ml-auto"
            onClick={onApply}
            disabled={filters.length === 0 || loading}
          >
            Apply
          </Button>
          <Button
            type="primary"
            danger
            className="ml-4"
            onClick={async() => {
              try {
                await axiosClient.get('/clear')
                setFilters([]);
                setImages([]);
              } catch (error) {
                console.log(error);
              }
            }}
            disabled={filters.length === 0 || loading}
          >
            Clear
          </Button>
          <Dropdown
            menu={{ items: dropdown }}
            className="ml-4"
            disabled={loading}
          >
            <Button className="bg-transparent">+</Button>
          </Dropdown>
        </div>
        {filters.map((filter) => {
          if (filter.type === "ocr")
            return (
              <div
                className="border-black border-solid border-[1px] rounded-md p-2"
                key={filter.id}
              >
                <div className="flex gap-4 items-center justify-between">
                  <div>OCR</div>
                  <Button
                    type="primary"
                    danger
                    onClick={() => onRemove(filter.id)}
                    disabled={loading}
                  >
                    Remove OCR
                  </Button>
                </div>
                <Input.TextArea
                  disabled={loading}
                  className="mt-4"
                  onChange={(e) =>
                    setFilters((prev) =>
                      prev.map(({ id, ...rest }) => {
                        if (filter.id !== id) return { id, ...rest };
                        return {
                          id: id,
                          label: e.target.value || "",
                          type: "ocr",
                        } as Filter;
                      })
                    )
                  }
                />
              </div>
            );
          return (
            <div
              className="border-black border-solid border-[1px] rounded-md p-2"
              key={filter.id}
            >
              <div className="flex gap-4 items-center justify-between">
                <div>Object</div>
                <Button
                  type="primary"
                  danger
                  onClick={() => onRemove(filter.id)}
                  disabled={loading}
                >
                  Remove Filter
                </Button>
              </div>
              <div className="mt-4">Label</div>
              <div className="w-full mt-4 flex gap-4">
                <InputNumber
                  disabled={filter.color.length >= 2 || loading}
                  controls={false}
                  min={1}
                  onChange={(val) => {
                    setFilters((prev) =>
                      prev.map(({ id, ...rest }) => {
                        if (filter.id !== id) return { id, ...rest };
                        return {
                          id: id,
                          ...rest,
                          qty: val,
                        };
                      })
                    );
                  }}
                />
                <Select
                  disabled={loading}
                  className="w-full"
                  options={labels.filter(
                    (label) =>
                      !filters.find((filter) => filter.label === label.value)
                  )}
                  showSearch
                  onChange={(val) =>
                    setFilters((prev) =>
                      prev.map(({ id, ...rest }) => {
                        if (filter.id !== id) return { id, ...rest };
                        return {
                          id: id,
                          ...rest,
                          label: val,
                        };
                      })
                    )
                  }
                />
              </div>
              <div className="mt-4">Color</div>
              {filter.color.map((color, index) => (
                <div className="flex gap-2 mt-4" key={color.id}>
                  <Select
                    disabled={loading}
                    options={colors}
                    mode="multiple"
                    className="w-full"
                    showSearch
                    onChange={(value: string[]) => {
                      setFilters((prev) =>
                        prev.map(({ id, ...rest }) => {
                          if (filter.id !== id) return { id, ...rest };
                          const { color: temp } = rest as { color: Color[] };
                          return {
                            id: id,
                            ...rest,
                            color: temp.map(({ id: colorId, ...rest }) => {
                              if (colorId !== color.id)
                                return { id: colorId, ...rest };
                              return {
                                id: colorId,
                                color: value,
                              } as Color;
                            }),
                          };
                        })
                      );
                    }}
                  />
                  <Button
                    type="primary"
                    danger
                    disabled={
                      (typeof filter.qty === "number" && index === 0) || loading
                    }
                    onClick={() => {
                      setFilters((prev) =>
                        prev.map(({ id, ...rest }) => {
                          if (filter.id !== id) return { id, ...rest };
                          const { color: temp } = rest as { color: Color[] };
                          return {
                            id: id,
                            ...rest,
                            color: temp.filter(({ id }) => id !== color.id),
                          };
                        })
                      );
                    }}
                  >
                    Delete
                  </Button>
                </div>
              ))}
              <Button
                disabled={
                  (typeof filter.qty === "number" &&
                    filter.color.length >= 1) ||
                  loading
                }
                type="primary"
                className="w-full mt-4"
                onClick={() => {
                  setFilters((prev) =>
                    prev.map(({ id, ...rest }) => {
                      if (filter.id !== id) return { id, ...rest };
                      const { color: temp } = rest as { color: Color[] };
                      return {
                        id: id,
                        ...rest,
                        color: [
                          ...temp,
                          { id: Date.now(), color: [] as string[] } as Color,
                        ],
                      };
                    })
                  );
                }}
              >
                Add color
              </Button>
            </div>
          );
        })}
      </div>
      <Drawer open={openCSV} onClose={() => setOpenCSV(false)} width={800}>
        <div className="relative max-h-full h-full overflow-hidden">
          <ul className="overflow-auto h-[calc(100%_-_48px)]">
            {submissions.length === 0 ? (
              <Empty />
            ) : (
              submissions.map((image, index) => (
                <li key={image.path}>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="mr-5">{index + 1}.</span>
                      {getFolder(image.path)}
                    </div>
                    <Button
                      danger
                      type="primary"
                      onClick={() => removeSubmission(image.path)}
                    >
                      Remove
                    </Button>
                  </div>
                  {index !== submissions.length - 1 && (
                    <div className="mb-4"></div>
                  )}
                </li>
              ))
            )}
          </ul>
          <div className="flex gap-4 mt-4 ml-auto bottom-0 justify-end">
            <Button
              type="default"
              danger
              className="bg-transparent"
              onClick={clearSubmission}
              disabled={submissions.length === 0}
            >
              Clear
            </Button>
            <Button
              type="primary"
              disabled={submissions.length === 0}
              onClick={downloadSubmission}
            >
              Download
            </Button>
          </div>
        </div>
      </Drawer>
    </>
  );
};

export default Header;
