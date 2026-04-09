use std::str::FromStr;

use harfrust::{Direction, Feature, Language, Script, Variation};
use pyo3::prelude::*;

// ---------------------------------------------------------------------------
// Direction
// ---------------------------------------------------------------------------

#[pyclass(name = "Direction", frozen, eq, hash, from_py_object)]
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub struct PyDirection(pub(crate) Direction);

#[pymethods]
impl PyDirection {
    #[new]
    fn new(s: &str) -> PyResult<Self> {
        Direction::from_str(s).map(PyDirection).map_err(|_| {
            pyo3::exceptions::PyValueError::new_err(format!("invalid direction: {s:?}"))
        })
    }

    #[classattr]
    const LTR: PyDirection = PyDirection(Direction::LeftToRight);

    #[classattr]
    const RTL: PyDirection = PyDirection(Direction::RightToLeft);

    #[classattr]
    const TTB: PyDirection = PyDirection(Direction::TopToBottom);

    #[classattr]
    const BTT: PyDirection = PyDirection(Direction::BottomToTop);

    fn __repr__(&self) -> &'static str {
        match self.0 {
            Direction::LeftToRight => "Direction.LTR",
            Direction::RightToLeft => "Direction.RTL",
            Direction::TopToBottom => "Direction.TTB",
            Direction::BottomToTop => "Direction.BTT",
            Direction::Invalid => "Direction(<invalid>)",
        }
    }

    fn __str__(&self) -> &'static str {
        match self.0 {
            Direction::LeftToRight => "ltr",
            Direction::RightToLeft => "rtl",
            Direction::TopToBottom => "ttb",
            Direction::BottomToTop => "btt",
            Direction::Invalid => "invalid",
        }
    }
}

// ---------------------------------------------------------------------------
// Script
// ---------------------------------------------------------------------------

#[pyclass(name = "Script", frozen, eq, hash, from_py_object)]
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub struct PyScript(pub(crate) Script);

#[pymethods]
impl PyScript {
    #[new]
    fn new(s: &str) -> PyResult<Self> {
        if s.len() != 4 || !s.bytes().all(|b| b.is_ascii_alphabetic()) {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "expected a 4-letter ISO 15924 script tag, got {s:?}"
            )));
        }
        Script::from_str(s)
            .map(PyScript)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err(format!("invalid script: {s:?}")))
    }

    #[getter]
    fn tag(&self) -> String {
        self.0.tag().to_string()
    }

    fn __repr__(&self) -> String {
        format!("Script(\"{}\")", self.0.tag())
    }

    fn __str__(&self) -> String {
        self.0.tag().to_string()
    }
}

// ---------------------------------------------------------------------------
// Language
// ---------------------------------------------------------------------------

#[pyclass(name = "Language", frozen, eq, hash, from_py_object)]
#[derive(Clone, PartialEq, Eq, Hash)]
pub struct PyLanguage(pub(crate) Language);

#[pymethods]
impl PyLanguage {
    #[new]
    fn new(s: &str) -> PyResult<Self> {
        Language::from_str(s).map(PyLanguage).map_err(|_| {
            pyo3::exceptions::PyValueError::new_err(format!("invalid language: {s:?}"))
        })
    }

    fn __repr__(&self) -> String {
        format!("Language(\"{}\")", self.0.as_str())
    }

    fn __str__(&self) -> String {
        self.0.as_str().to_string()
    }
}

// ---------------------------------------------------------------------------
// Feature
// ---------------------------------------------------------------------------

#[pyclass(name = "Feature", frozen, eq, hash, from_py_object)]
#[derive(Clone, Copy, PartialEq, Hash)]
pub struct PyFeature(pub(crate) Feature);

#[pymethods]
impl PyFeature {
    #[new]
    fn new(s: &str) -> PyResult<Self> {
        Feature::from_str(s)
            .map(PyFeature)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err(format!("invalid feature: {s:?}")))
    }

    #[getter]
    fn tag(&self) -> String {
        self.0.tag.to_string()
    }

    #[getter]
    fn value(&self) -> u32 {
        self.0.value
    }

    #[getter]
    fn start(&self) -> u32 {
        self.0.start
    }

    #[getter]
    fn end(&self) -> u32 {
        self.0.end
    }

    fn __repr__(&self) -> String {
        let tag = self.0.tag;
        let val = self.0.value;
        let start = self.0.start;
        let end = self.0.end;
        if start == 0 && end == u32::MAX {
            if val == 1 {
                format!("Feature(\"+{tag}\")")
            } else if val == 0 {
                format!("Feature(\"-{tag}\")")
            } else {
                format!("Feature(\"{tag}={val}\")")
            }
        } else {
            format!("Feature(\"{tag}[{start}:{end}]={val}\")")
        }
    }

    fn __str__(&self) -> String {
        let tag = self.0.tag;
        let val = self.0.value;
        let start = self.0.start;
        let end = self.0.end;
        if start == 0 && end == u32::MAX {
            if val == 1 {
                format!("+{tag}")
            } else if val == 0 {
                format!("-{tag}")
            } else {
                format!("{tag}={val}")
            }
        } else {
            format!("{tag}[{start}:{end}]={val}")
        }
    }
}

// ---------------------------------------------------------------------------
// Variation
// ---------------------------------------------------------------------------

#[pyclass(name = "Variation", frozen, eq, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyVariation(pub(crate) Variation);

#[pymethods]
impl PyVariation {
    #[new]
    fn new(s: &str) -> PyResult<Self> {
        Variation::from_str(s).map(PyVariation).map_err(|_| {
            pyo3::exceptions::PyValueError::new_err(format!("invalid variation: {s:?}"))
        })
    }

    #[getter]
    fn tag(&self) -> String {
        self.0.tag.to_string()
    }

    #[getter]
    fn value(&self) -> f32 {
        self.0.value
    }

    fn __repr__(&self) -> String {
        format!("Variation(\"{}={}\")", self.0.tag, self.0.value)
    }

    fn __str__(&self) -> String {
        format!("{}={}", self.0.tag, self.0.value)
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDirection>()?;
    m.add_class::<PyScript>()?;
    m.add_class::<PyLanguage>()?;
    m.add_class::<PyFeature>()?;
    m.add_class::<PyVariation>()?;
    Ok(())
}
