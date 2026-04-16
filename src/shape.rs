use pyo3::prelude::*;

#[pyfunction]
#[pyo3(signature = (font_path, text, options=""))]
fn shape(font_path: &str, text: &str, options: &str) -> PyResult<String> {
    hr_shape::shape(font_path, text, options)
        .map(|s| s.trim_end().to_string())
        .map_err(pyo3::exceptions::PyRuntimeError::new_err)
}

#[pyfunction]
fn run_from_args(args: Vec<String>) -> PyResult<String> {
    hr_shape::run_from_args(args)
        .map(|s| s.trim_end().to_string())
        .map_err(pyo3::exceptions::PyRuntimeError::new_err)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(shape, m)?)?;
    m.add_function(wrap_pyfunction!(run_from_args, m)?)?;
    Ok(())
}
