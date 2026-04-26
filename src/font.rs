use std::str::FromStr;

use harfrust::{Feature, FontRef, Shaper, ShaperData, ShaperInstance, Variation};
use pyo3::exceptions::{PyRuntimeError, PyTypeError, PyValueError};
use pyo3::prelude::*;

use crate::buffer::PyBuffer;
use crate::glyph::PyGlyphBuffer;
use crate::types::{PyFeature, PyVariation};

#[pyclass(name = "Font", unsendable)]
pub struct PyFont {
    data: Vec<u8>,
    face_index: u32,
    shaper_data: ShaperData,
    instance: Option<ShaperInstance>,
    point_size: Option<f32>,
}

impl PyFont {
    fn build_from_bytes(data: Vec<u8>, face_index: u32) -> PyResult<Self> {
        // Validate the font and build ShaperData up front so subsequent calls
        // don't need to re-parse. ShaperData is 'static — it borrows FontRef
        // only during construction.
        let shaper_data = {
            let font = FontRef::from_index(&data, face_index)
                .map_err(|e| PyRuntimeError::new_err(format!("failed to parse font: {e}")))?;
            ShaperData::new(&font)
        };
        Ok(Self {
            data,
            face_index,
            shaper_data,
            instance: None,
            point_size: None,
        })
    }

    pub(crate) fn font_ref(&self) -> PyResult<FontRef<'_>> {
        FontRef::from_index(&self.data, self.face_index)
            .map_err(|e| PyRuntimeError::new_err(format!("failed to parse font: {e}")))
    }

    pub(crate) fn build_shaper<'a>(&'a self, font: &FontRef<'a>) -> Shaper<'a> {
        self.shaper_data
            .shaper(font)
            .instance(self.instance.as_ref())
            .point_size(self.point_size)
            .build()
    }
}

#[pymethods]
impl PyFont {
    #[new]
    #[pyo3(signature = (path, face_index=0))]
    fn new(path: &str, face_index: u32) -> PyResult<Self> {
        let data = std::fs::read(path)
            .map_err(|e| PyRuntimeError::new_err(format!("failed to read {path:?}: {e}")))?;
        Self::build_from_bytes(data, face_index)
    }

    #[staticmethod]
    #[pyo3(signature = (data, face_index=0))]
    fn from_bytes(data: Vec<u8>, face_index: u32) -> PyResult<Self> {
        Self::build_from_bytes(data, face_index)
    }

    #[getter]
    fn face_index(&self) -> u32 {
        self.face_index
    }

    #[getter]
    fn units_per_em(&self) -> PyResult<i32> {
        let font = self.font_ref()?;
        Ok(self.build_shaper(&font).units_per_em())
    }

    fn set_variations(&mut self, variations: &Bound<'_, PyAny>) -> PyResult<()> {
        let vars = parse_variations(variations)?;
        if vars.is_empty() {
            self.instance = None;
            return Ok(());
        }
        // Direct field access (rather than self.font_ref()) so the borrow
        // checker can split self.data (immutable) from self.instance (mutable).
        let font = FontRef::from_index(&self.data, self.face_index)
            .map_err(|e| PyRuntimeError::new_err(format!("failed to parse font: {e}")))?;
        match &mut self.instance {
            Some(inst) => inst.set_variations(&font, vars),
            None => {
                self.instance = Some(ShaperInstance::from_variations(&font, vars));
            }
        }
        Ok(())
    }

    #[pyo3(signature = (size))]
    fn set_point_size(&mut self, size: Option<f32>) {
        self.point_size = size;
    }

    #[pyo3(signature = (buffer, features=None))]
    fn shape(
        &self,
        buffer: &mut PyBuffer,
        features: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<PyGlyphBuffer> {
        let feats = match features {
            Some(any) => parse_features(any)?,
            None => Vec::new(),
        };
        // Reject Invalid direction up front — harfrust panics on it otherwise,
        // surfacing as PanicException in Python instead of a clean error.
        if buffer.as_ref_buf()?.direction() == harfrust::Direction::Invalid {
            return Err(PyValueError::new_err(
                "buffer direction is unset; call buffer.guess_segment_properties() \
                 or assign buffer.direction before shaping",
            ));
        }
        let inner = buffer.take_inner()?;
        let font = self.font_ref()?;
        let shaper = self.build_shaper(&font);
        Ok(PyGlyphBuffer::wrap(shaper.shape(inner, &feats)))
    }

    fn __repr__(&self) -> String {
        format!(
            "Font(face_index={}, bytes={})",
            self.face_index,
            self.data.len()
        )
    }
}

fn parse_features(any: &Bound<'_, PyAny>) -> PyResult<Vec<Feature>> {
    if let Ok(s) = any.extract::<&str>() {
        return parse_csv(s, "feature", Feature::from_str);
    }
    if let Ok(seq) = any.extract::<Vec<PyFeature>>() {
        return Ok(seq.into_iter().map(|f| f.0).collect());
    }
    Err(PyTypeError::new_err(
        "expected a sequence of Feature objects or a string",
    ))
}

fn parse_variations(any: &Bound<'_, PyAny>) -> PyResult<Vec<Variation>> {
    if let Ok(s) = any.extract::<&str>() {
        return parse_csv(s, "variation", Variation::from_str);
    }
    if let Ok(seq) = any.extract::<Vec<PyVariation>>() {
        return Ok(seq.into_iter().map(|v| v.0).collect());
    }
    Err(PyTypeError::new_err(
        "expected a sequence of Variation objects or a string",
    ))
}

fn parse_csv<T, E>(s: &str, label: &str, parse: impl Fn(&str) -> Result<T, E>) -> PyResult<Vec<T>> {
    let mut out = Vec::new();
    for piece in s.split(',') {
        let piece = piece.trim();
        if piece.is_empty() {
            continue;
        }
        let value = parse(piece)
            .map_err(|_| PyValueError::new_err(format!("invalid {label}: {piece:?}")))?;
        out.push(value);
    }
    Ok(out)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFont>()?;
    Ok(())
}
