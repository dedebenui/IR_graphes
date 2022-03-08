
#ifdef _DEBUG
#undef _DEBUG
#include <python.h>
#define _DEBUG
#else
#include <python.h>
#endif


#include <pybind11/embed.h>
#include <iostream>

namespace py = pybind11;

int main() {
    wchar_t* home_dir = Py_DecodeLocale("python", nullptr);
    Py_SetPythonHome(home_dir);

    py::initialize_interpreter();
    PyEval_SaveThread();

    auto state = PyGILState_Ensure();

    try {
        auto emsapp = py::module::import("python.emsapp.emsapp");
        emsapp.attr("main")();
    }
    catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        PyGILState_Release(state);
        return -1;
    }
    PyGILState_Release(state);

    return 0;
}